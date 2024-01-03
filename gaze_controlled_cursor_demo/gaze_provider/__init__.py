from pupil_labs.realtime_api.simple import discover_one_device
from pupil_labs.real_time_screen_gaze.gaze_mapper import GazeMapper
from pupil_labs.real_time_screen_gaze import marker_generator

import pyautogui


class DummyGazeProvider:
    def __init__(self, markers=None, screen_size=None):
        pass

    @property
    def connected(self):
        return True

    def connect(self):
        return True

    def receive(self):
        """The device must be connected and a surface must be defined before calling this method."""
        import time

        p = pyautogui.position()
        # TODO: For some reason the resolution of the app is not actually equal to the screen resolution. You have to devide it by the primaryScreen.devicePixelRatio() to correctly place it.
        p = p[0] / 1.25, p[1] / 1.25
        return p, time.time()

    @classmethod
    def generate_marker(cls, marker_id):
        return marker_generator.generate_marker(marker_id, flip_x=True, flip_y=True)

    def close(self):
        pass


class GazeProvider:
    def __init__(self, markers, screen_size):
        self.markers = markers
        self.screen_size = screen_size

        self.device = None
        self.gazeMapper = None
        self.surface_definition = None
        self.surface = None

    @property
    def connected(self):
        return self.device is not None

    def connect(self):
        if self.device is not None:
            print("Already connected to device")
            return

        self.device = discover_one_device(max_search_duration_seconds=10)

        if self.device is None:
            print("Connection attempt to device failed")
            return False
        print("Connected to device")

        calibration = self.device.get_calibration()
        self.gazeMapper = GazeMapper(calibration)

        verts = {
            i: self.markers[i].get_marker_verts() for i in range(len(self.markers))
        }
        self.surface = self.gazeMapper.add_surface(verts, self.screen_size)

        return True

    def receive(self):
        """The device must be connected and a surface must be defined before calling this method."""
        assert self.device is not None
        assert self.surface is not None

        frame, raw_gaze, eyes = self._receive_data_from_device()
        mapped_gaze, detected_markers = self._map_gaze(frame, raw_gaze)

        return mapped_gaze, raw_gaze.timestamp_unix_seconds

    def _receive_data_from_device(self):
        scene_and_gaze = self.device.receive_matched_scene_video_frame_and_gaze(
            timeout_seconds=1 / 15
        )

        if scene_and_gaze is None:
            raise ValueError("No scene frame and gaze received")

        eyes = self.device.receive_eyes_video_frame(timeout_seconds=1 / 15)

        if eyes is None:
            raise ValueError("No eye video frame received")

        (
            scene,
            gaze,
        ) = scene_and_gaze
        return scene, gaze, eyes

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
        if self.device is not None:
            self.device.close()
