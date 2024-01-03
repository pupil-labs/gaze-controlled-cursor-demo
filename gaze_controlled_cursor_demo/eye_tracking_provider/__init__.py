from collections import namedtuple

from pupil_labs.real_time_screen_gaze.gaze_mapper import GazeMapper
from pupil_labs.real_time_screen_gaze import marker_generator
from .raw_data_receiver import RawDataReceiver

from .marker import Marker


EyeTrackingData = namedtuple(
    "EyeTrackingData", ["timestamp", "gaze", "detected_markers"]
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

    def receive(self) -> EyeTrackingData:
        raw_data = self.raw_data_receiver.receive()

        mapped_gaze, detected_markers = self._map_gaze(
            raw_data.scene, raw_data.raw_gaze
        )

        eye_tracking_data = EyeTrackingData(
            raw_data.raw_gaze.timestamp_unix_seconds, mapped_gaze, detected_markers
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
        pass

    def receive(self) -> EyeTrackingData:
        import time
        import pyautogui

        p = pyautogui.position()
        # TODO: For some reason the resolution of the app is not actually equal to the screen resolution. You have to devide it by the primaryScreen.devicePixelRatio() to correctly place it.
        p = p[0] / 1.25, p[1] / 1.25

        eye_tracking_data = EyeTrackingData(time.time(), p, [])

        return eye_tracking_data

    def close(self):
        pass
