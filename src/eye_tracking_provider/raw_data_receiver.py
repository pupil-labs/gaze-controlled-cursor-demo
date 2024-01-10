import sys
from collections import namedtuple

from pupil_labs.realtime_api.simple import discover_one_device, Device


RawETData = namedtuple("RawETData", ["raw_gaze", "scene", "eyes"])


class RawDataReceiver:
    def __init__(self):
        self.device = None

    @property
    def scene_calibration(self):
        return self.device.get_calibration()

    def connect(self, auto_discover=False, ip=None, port=None):
        assert auto_discover or (ip is not None and port is not None)

        if self.device is not None:
            self.device.close()

        try:
            if auto_discover:
                print("Connecting to device...")
                self.device = discover_one_device()
                print("\rdone")
            else:
                print(f"Connecting to device at {ip}:{port}...")
                self.device = Device(ip, port)
                print("\rdone")
        except Exception as exc:
            print(exc, file=sys.stderr)
            self.device = None

        if self.device is None:
            return None
        else:
            return self.device.phone_ip, self.device.port

    def receive(self):
        if self.device is None:
            return None

        scene_and_gaze = self.device.receive_matched_scene_video_frame_and_gaze(
            timeout_seconds=1 / 15
        )
        if scene_and_gaze is None:
            return None

        eyes = self.device.receive_eyes_video_frame(timeout_seconds=1 / 15)
        if eyes is None:
            return None

        (
            scene,
            gaze,
        ) = scene_and_gaze

        return RawETData(gaze, scene, eyes)

    def close(self):
        if self.device is not None:
            self.device.close()
