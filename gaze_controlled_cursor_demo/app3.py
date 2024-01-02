import sys
import json

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import pyautogui
import time

from ui import MainWindow


from gaze_provider import GazeProvider as GazeProvider

pyautogui.FAILSAFE = False


class GazeControllApp(QApplication):
    def __init__(self):
        super().__init__()
        self.gaze_provider = GazeProvider()

        self.main_window = MainWindow()
        self.main_window.layout().addWidget(self.gaze_provider.marker_widget)

        self.setApplicationDisplayName("Gaze Control")

        self.pollTimer = QTimer()
        self.pollTimer.setInterval(1000 / 30)
        self.pollTimer.timeout.connect(self.poll)

        self.gaze_location = None

    def onSurfaceChanged(self):
        self.updateSurface()

    def updateSurface(self):
        if self.gazeMapper is None:
            return

        self.gazeMapper.clear_surfaces()
        self.surface = self.gazeMapper.add_surface(
            self.marker_widget.getMarkerVerts(), self.marker_widget.getSurfaceSize()
        )

    def start(self):
        self.gaze_provider.connect()
        if not self.gaze_provider.connected:
            QTimer.singleShot(1000, self.start)
            return

        self.pollTimer.start()
        pass

    def setMouseEnabled(self, enabled):
        self.mouseEnabled = enabled

    def poll(self):
        gaze, timestamp = self.gaze_provider.receive()
        self.main_window.update_gaze(gaze)

    def exec(self):
        self.main_window.showMaximized()
        QTimer.singleShot(1000, self.start)
        super().exec()
        self.gaze_provider.close()


def run():
    app = GazeControllApp()
    app.exec()
