from collections import namedtuple

from pupil_labs.realtime_api.simple import discover_one_device


RawETData = namedtuple("RawETData", ["raw_gaze", "scene", "eyes"])


class RawDataReceiver:
    def __init__(self):
        print("Connecting to device...")
        self.device = discover_one_device()
        print("\rdone")

    @property
    def scene_calibration(self):
        return self.device.get_calibration()

    def receive(self):
        assert self.device is not None

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

        return RawETData(gaze, scene, eyes)

    def close(self):
        if self.device is not None:
            self.device.close()
