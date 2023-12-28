from pupil_labs.realtime_api.simple import discover_one_device
from pupil_labs.real_time_screen_gaze.gaze_mapper import GazeMapper


class GazeProvider:
    def __init__(self):
        self.device = None
        self.gazeMapper = None
        self.surface_definition = None
        self.surface = None
        surface_to_screen_transform = None

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

        if self.surface_definition is not None:
            self.updateSurface(
                self.surface_definition["marker_verts"],
                self.surface_definition["surface_size"],
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

        device_response = self.device.receive_matched_scene_video_frame_and_gaze(
            timeout_seconds=1 / 15
        )

        if device_response is None:
            print("No frame and gaze")
            return None

        frame, gaze = device_response
        result = self.gazeMapper.process_frame(frame, gaze)

        detected_markers = [int(marker.uid.split(":")[-1]) for marker in result.markers]
        gaze = None

        if self.surface.uid in result.mapped_gaze:
            for surface_gaze in result.mapped_gaze[self.surface.uid]:
                gaze = surface_gaze.x, surface_gaze.y

        return gaze, detected_markers
