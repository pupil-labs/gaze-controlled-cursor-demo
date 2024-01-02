import sys
import json

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import pyautogui
import time

from ui import MainWindow


from gaze_provider import GazeProvider as GazeProvider
from dwell_detector import DwellDetector

pyautogui.FAILSAFE = False


class GazeControllApp(QApplication):
    def __init__(self):
        super().__init__()

        self.main_window = MainWindow()

        screen_size = self.primaryScreen().size()
        screen_size = (screen_size.width(), screen_size.height())
        self.gaze_provider = GazeProvider(
            markers=self.main_window.markers, screen_size=screen_size
        )

        self.dwell_detector = DwellDetector(0.5, 75)

        self.setApplicationDisplayName("Gaze Control")

        self.pollTimer = QTimer()
        self.pollTimer.setInterval(1000 / 30)
        self.pollTimer.timeout.connect(self.poll)

        self.gaze_location = None

    def start(self):
        self.gaze_provider.connect()
        if not self.gaze_provider.connected:
            QTimer.singleShot(1000, self.start)

        self.pollTimer.start()
        pass

    def poll(self):
        gaze, timestamp = self.gaze_provider.receive()
        dwell_process = self.dwell_detector.addPoint(gaze, timestamp)

        self.main_window.update_gaze(gaze, dwell_process)

        # pyautogui.moveTo(*gaze)

        # if dwell_process == 1.0:
        #     pyautogui.click()

    def exec(self):
        self.main_window.showMaximized()
        QTimer.singleShot(1000, self.start)
        super().exec()
        self.gaze_provider.close()


def run():
    app = GazeControllApp()
    app.exec()
