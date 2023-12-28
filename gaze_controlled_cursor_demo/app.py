import sys
import json

from pupil_labs.realtime_api.simple import discover_one_device
from pupil_labs.real_time_screen_gaze.gaze_mapper import GazeMapper

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import pyautogui
import time

from ui import TagWindow
from dwell_detector import DwellDetector
from gaze_provider import GazeProvider

pyautogui.FAILSAFE = False


class PupilPointerApp(QApplication):
    def __init__(self):
        super().__init__()

        self.gaze_provider = GazeProvider()

        self.setApplicationDisplayName("Pupil Pointer")
        self.mouseEnabled = False

        self.tagWindow = TagWindow()

        self.dwellDetector = DwellDetector(0.75, 75)
        self.smoothing = 0.8

        self.tagWindow.surfaceChanged.connect(self.onSurfaceChanged)

        self.tagWindow.dwellTimeChanged.connect(self.dwellDetector.setDuration)
        self.tagWindow.dwellRadiusChanged.connect(self.dwellDetector.setRange)
        self.tagWindow.mouseEnableChanged.connect(self.setMouseEnabled)
        self.tagWindow.smoothingChanged.connect(self.setSmoothing)

        self.pollTimer = QTimer()
        self.pollTimer.setInterval(1000 / 30)
        self.pollTimer.timeout.connect(self.poll)

        self.surface = None
        self.firstPoll = True

        self.mousePosition = None
        self.gazeMapper = None

    def onSurfaceChanged(self):
        self.updateSurface()

    def start(self):
        if not self.gaze_provider.connected:
            QTimer.singleShot(1000, self.gaze_provider.connect)
            return

        marker_verts = self.tagWindow.getMarkerVerts()
        surface_size = self.tagWindow.getSurfaceSize()
        self.gaze_provider.updateSurface(marker_verts, surface_size)
        self.pollTimer.start()

    def setMouseEnabled(self, enabled):
        self.mouseEnabled = enabled

    def poll(self):
        gaze, detected_markers = self.gaze_provider.receive()
        self.tagWindow.showMarkerFeedback(detected_markers)

        self.mousePosition = [gaze[0], gaze[1]]

        mousePoint = self.tagWindow.updatePoint(*self.mousePosition)

        changed, dwell, dwellPosition = self.dwellDetector.addPoint(
            mousePoint.x(), mousePoint.y(), gaze.timestamp_unix_seconds
        )
        if changed and dwell:
            self.tagWindow.setClicked(True)
            if self.mouseEnabled:
                pyautogui.click(x=dwellPosition[0], y=dwellPosition[1])
        else:
            self.tagWindow.setClicked(False)

        if self.mouseEnabled:
            QCursor().setPos(mousePoint)

        self.mousePosition = pyautogui.position()
        mousePoint = self.tagWindow.updatePoint(
            *self.mousePosition, self.dwellDetector.dwellProcess
        )
        changed, dwell, dwellPosition = self.dwellDetector.addPoint(
            mousePoint.x(), mousePoint.y(), time.time()
        )
        if changed and dwell:
            self.tagWindow.setClicked(True)
            if self.mouseEnabled:
                pyautogui.click(x=dwellPosition[0], y=dwellPosition[1])
        else:
            self.tagWindow.setClicked(False)

        if self.mouseEnabled:
            QCursor().setPos(mousePoint)

    def exec(self):
        self.tagWindow.setStatus("Looking for a device...")
        self.tagWindow.showMaximized()
        QTimer.singleShot(1000, self.start)
        super().exec()
        if self.device is not None:
            self.device.close()


def run():
    app = PupilPointerApp()
    app.exec()
