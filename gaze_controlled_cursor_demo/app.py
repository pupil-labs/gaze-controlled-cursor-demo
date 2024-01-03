import sys
import json

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import pyautogui
import time

from ui import MainWindow


from eye_tracking_provider import DummyEyeTrackingProvider as EyeTrackingProvider

pyautogui.FAILSAFE = False


class GazeControllApp(QApplication):
    def __init__(self):
        super().__init__()
        screen_size = self.primaryScreen().size()
        self.main_window = MainWindow(screen_size)

        screen_size = (screen_size.width(), screen_size.height())
        self.eye_tracking_provider = EyeTrackingProvider(
            markers=self.main_window.markers, screen_size=screen_size
        )

        self.setApplicationDisplayName("Gaze Control")

        self.pollTimer = QTimer()
        self.pollTimer.setInterval(1000 / 30)
        self.pollTimer.timeout.connect(self.poll)
        self.pollTimer.start()

        self.gaze_location = None

    def poll(self):
        eye_tracking_data = self.eye_tracking_provider.receive()

        self.main_window.update_gaze(
            eye_tracking_data.gaze, eye_tracking_data.dwell_process
        )

        # pyautogui.moveTo(*gaze)

        # if dwell_process == 1.0:
        #     pyautogui.click()

    def exec(self):
        self.main_window.show()
        super().exec()
        self.eye_tracking_provider.close()


def run():
    app = GazeControllApp()
    app.exec()
