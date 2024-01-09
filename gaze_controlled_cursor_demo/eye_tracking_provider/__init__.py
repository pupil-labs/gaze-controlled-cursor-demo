from collections import namedtuple
import numpy as np

from pupil_labs.real_time_screen_gaze.gaze_mapper import GazeMapper

from .raw_data_receiver import RawDataReceiver
from .marker import Marker
from .dwell_detector import DwellDetector


EyeTrackingData = namedtuple(
    "EyeTrackingData",
    ["timestamp", "gaze", "detected_markers", "dwell_process", "scene", "raw_gaze"],
)


class EyeTrackingProvider:
    def __init__(self, markers, screen_size):
        self.markers = markers
        self.screen_size = screen_size

        self.raw_data_receiver = RawDataReceiver()

        self.gazeMapper = GazeMapper(self.raw_data_receiver.scene_calibration)
        verts = {
            i: self.markers[i].get_marker_verts() for i in range(len(self.markers))
        }
        self.surface = self.gazeMapper.add_surface(verts, self.screen_size)

        self.dwell_detector = DwellDetector(0.5, 75)

    def update_surface(self):
        self.gazeMapper.clear_surfaces()
        verts = {
            i: self.markers[i].get_marker_verts() for i in range(len(self.markers))
        }
        self.surface = self.gazeMapper.add_surface(verts, self.screen_size)

    def receive(self) -> EyeTrackingData:
        raw_data = self.raw_data_receiver.receive()

        if raw_data is None:
            return None

        mapped_gaze, detected_markers = self._map_gaze(
            raw_data.scene, raw_data.raw_gaze
        )

        dwell_process = self.dwell_detector.addPoint(
            mapped_gaze, raw_data.raw_gaze.timestamp_unix_seconds
        )

        eye_tracking_data = EyeTrackingData(
            raw_data.raw_gaze.timestamp_unix_seconds,
            mapped_gaze,
            detected_markers,
            dwell_process,
            raw_data.scene,
            raw_data.raw_gaze,
        )

        return eye_tracking_data

    def _map_gaze(self, frame, gaze):
        assert self.surface is not None

        result = self.gazeMapper.process_frame(frame, gaze)

        detected_markers = [int(marker.uid.split(":")[-1]) for marker in result.markers]
        gaze = None

        if self.surface.uid in result.mapped_gaze:
            for surface_gaze in result.mapped_gaze[self.surface.uid]:
                gaze = surface_gaze.x, surface_gaze.y
                gaze = (
                    gaze[0] * self.screen_size[0],
                    (1 - gaze[1]) * self.screen_size[1],
                )

        return gaze, detected_markers

    def close(self):
        self.raw_data_receiver.close()


class DummyEyeTrackingProvider:
    def __init__(self, markers, screen_size):
        self.dwell_detector = DwellDetector(0.5, 75)

    def receive(self) -> EyeTrackingData:
        import time
        import pyautogui

        ts = time.time()

        p = pyautogui.position()
        # TODO: For some reason the resolution of the app is not actually equal to the screen resolution. You have to devide it by the primaryScreen.devicePixelRatio() to correctly place it.
        p = p[0] / 1.25, p[1] / 1.25

        dwell_process = self.dwell_detector.addPoint(p, ts)

        scene_img = np.zeros((1600, 1200, 3), dtype=np.uint8)
        scene = type("", (object,), {"bgr_pixels": scene_img})()

        eye_tracking_data = EyeTrackingData(ts, p, [], dwell_process, scene)

        return eye_tracking_data

    def update_surface(self):
        pass

    def close(self):
        pass
