import cv2
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from eye_tracking_provider import EyeTrackingProvider


class Marker:
    def __init__(self, verts):
        self.verts = verts

    def get_marker_verts(self):
        return self.verts


markers = [
    Marker([(0.0, 0.0), (0.0, 100.0), (100.0, 0.0), (100.0, 100.0)]) for i in range(4)
]

screen_size = (1920.0, 1080.0)

receiver = EyeTrackingProvider(markers, screen_size)

while True:
    try:
        data = receiver.receive()
    except ValueError:
        continue

    scene = data.scene.bgr_pixels

    cv2.imshow("scene", scene)
    cv2.waitKey(1)
