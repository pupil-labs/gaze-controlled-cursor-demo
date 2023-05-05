import asyncio

from pupil_labs.realtime_api.simple import discover_one_device

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import pyautogui

from . import cloud_api
from .ui import TagWindow
from .screen_mapper import ScreenMapper
from .dwell_detector import DwellDetector

pyautogui.FAILSAFE = False

class PupilPointerApp(QApplication):
    def __init__(self):
        super().__init__()

        self.setApplicationDisplayName('Pupil Pointer')
        self.mouseEnabled = False

        self.tagWindow = TagWindow()

        self.device = None
        self.dwellDetector = DwellDetector(.75, 75)

        self.tagWindow.surfaceChanged.connect(self.onSurfaceChanged)

        self.tagWindow.dwellTimeChanged.connect(self.dwellDetector.setDuration)
        self.tagWindow.dwellRadiusChanged.connect(self.dwellDetector.setRange)
        self.tagWindow.mouseEnableChanged.connect(self.setMouseEnabled)


        self.pollTimer = QTimer()
        self.pollTimer.setInterval(1000/200)
        self.pollTimer.timeout.connect(self.poll)

        self.screenMapper = ScreenMapper(None)

        self.camera = None
        self.surface0 = None
        self.firstPoll = True

    def onSurfaceChanged(self):
        self.updateSurface()

    def start(self):
        self.device = discover_one_device(max_search_duration_seconds=0.25)

        if self.device is None:
            QTimer.singleShot(1000, self.start)
            return

        if not self.device.serial_number_scene_cam:
            self.tagWindow.setStatus(f'Camera not connected on device {self.device}')
            QTimer.singleShot(1000, self.start)
            return

        self.tagWindow.setStatus(f'Connected to {self.device}. One moment...')

        self.setupScreenMapper()
        self.pollTimer.start()
        self.firstPoll = True

    def setupScreenMapper(self):
        self.camera = cloud_api.camera_for_scene_cam_serial(self.device.serial_number_scene_cam)
        self.screenMapper.camera = self.camera
        self.updateSurface()

    def updateSurface(self):
        self.surface0 = self.screenMapper.set_screen_surface(
            self.tagWindow.getMarkerSize(),
            self.tagWindow.getSurfaceSize()
        )

    def setMouseEnabled(self, enabled):
        self.mouseEnabled = enabled

    def poll(self):
        if self.firstPoll:
            timeout = 5
            self.firstPoll = False
        else:
            timeout = 0.1

        frame_and_gaze = self.device.receive_matched_scene_video_frame_and_gaze(timeout_seconds=timeout)

        if frame_and_gaze is None:
            self.tagWindow.setStatus(f'Failed to receive data from {self.device}')
            return
        else:
            self.tagWindow.setStatus(f'Streaming data from {self.device}')

        frame, gaze = frame_and_gaze
        result = self.screenMapper.process_frame(frame, gaze)

        markerIds = [int(marker.uid.split(':')[-1]) for marker in result.markers]
        self.tagWindow.showMarkerFeedback(markerIds)

        if self.surface0.uid in result.mapped_gaze:
            for surface_gaze in result.mapped_gaze[self.surface0.uid]:
                mousePoint = self.tagWindow.updatePoint(surface_gaze.x, surface_gaze.y)

                changed, dwell, dwellPosition = self.dwellDetector.addPoint(mousePoint.x(), mousePoint.y(), gaze.timestamp_unix_seconds)
                if changed and dwell:
                    self.tagWindow.setClicked(True)
                    if self.mouseEnabled:
                        pyautogui.click(x=dwellPosition[0], y=dwellPosition[1])
                else:
                    self.tagWindow.setClicked(False)

                if self.mouseEnabled:
                    QCursor().setPos(mousePoint)

    def exec(self):
        self.tagWindow.setStatus('Looking for a device...')
        self.tagWindow.showMaximized()
        QTimer.singleShot(1000, self.start)
        super().exec()
        if self.device is not None:
            self.device.close()

def run():
    app = PupilPointerApp()
    app.exec()
