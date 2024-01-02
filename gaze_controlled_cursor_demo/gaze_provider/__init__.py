from pupil_labs.realtime_api.simple import discover_one_device
from pupil_labs.real_time_screen_gaze.gaze_mapper import GazeMapper
from pupil_labs.real_time_screen_gaze import marker_generator

from .marker_widget import MarkerWidget
from PySide6.QtCore import QPoint

# TODO make detected markers a property


class DummyGazeProvider:
    def __init__(self):
        # self.device = None
        # self.gazeMapper = None
        # self.surface_definition = None
        # self.surface = None
        # self.surface_to_global_transform = surface_to_global_transform
        self.marker_widget = MarkerWidget()

    @property
    def connected(self):
        return True

    def connect(self):
        return True

    def receive(self):
        """The device must be connected and a surface must be defined before calling this method."""
        import time

        gaze = QPoint(1000, 500)
        return gaze, time.time()

    @classmethod
    def generate_marker(cls, marker_id):
        return marker_generator.generate_marker(marker_id, flip_x=True, flip_y=True)

    def close(self):
        pass


class GazeProvider:
    def __init__(self):
        self.device = None
        self.gazeMapper = None
        self.surface_definition = None
        self.surface = None

        self.marker_widget = MarkerWidget()

    @property
    def connected(self):
        return self.device is not None

    def connect(self):
        if self.device is not None:
            print("Already connected to device")
            return

        self.device = discover_one_device(max_search_duration_seconds=0.25)

        if self.device is None:
            print("Connection attempt to device failed")
            return False
        print("Connected to device")

        calibration = self.device.get_calibration()
        self.gazeMapper = GazeMapper(calibration)
        self.surface = self.gazeMapper.add_surface(
            self.marker_widget.getMarkerVerts(), self.marker_widget.getSurfaceSize()
        )

        return True

    def updateSurface(self, marker_verts, surface_size):
        self.surface_definition = {
            "marker_verts": marker_verts,
            "surface_size": surface_size,
        }

        if self.gazeMapper is not None:
            self.gazeMapper.clear_surfaces()
            self.surface = self.gazeMapper.add_surface(marker_verts, surface_size)

    def receive(self):
        """The device must be connected and a surface must be defined before calling this method."""
        assert self.device is not None
        assert self.surface is not None

        frame, raw_gaze = self._receive_data_from_device()
        mapped_gaze, detected_markers = self._map_gaze(frame, raw_gaze)
        if mapped_gaze is not None:
            mapped_gaze = self.marker_widget.surface_to_global_transform(*mapped_gaze)

        return mapped_gaze, raw_gaze.timestamp_unix_seconds

    def _receive_data_from_device(self):
        device_response = self.device.receive_matched_scene_video_frame_and_gaze(
            timeout_seconds=1 / 15
        )

        if device_response is None:
            raise ValueError("No frame and gaze received")

        frame, gaze = device_response
        return frame, gaze

    def _map_gaze(self, frame, gaze):
        assert self.surface is not None

        result = self.gazeMapper.process_frame(frame, gaze)

        detected_markers = [int(marker.uid.split(":")[-1]) for marker in result.markers]
        gaze = None

        if self.surface.uid in result.mapped_gaze:
            for surface_gaze in result.mapped_gaze[self.surface.uid]:
                gaze = surface_gaze.x, surface_gaze.y

        return gaze, detected_markers

    @classmethod
    def generate_marker(cls, marker_id):
        return marker_generator.generate_marker(marker_id, flip_x=True, flip_y=True)

    def close(self):
        if self.device is not None:
            self.device.close()
