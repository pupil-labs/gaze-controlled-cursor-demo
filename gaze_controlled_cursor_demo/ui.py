import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent, QResizeEvent
from PySide6.QtWidgets import *

from eye_tracking_provider import Marker
from marker_overlay import MarkerOverlay
from gaze_overlay import GazeOverlay
from keyboard import Keyboard
import utils


class MainWindow(QWidget):
    def __init__(self, screen_size):
        super().__init__()

        self.setFixedSize(screen_size)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")

        # Make window transparent for mouse events such that any click will be passed through to the window below.
        self.setWindowFlag(Qt.WindowTransparentForInput)

        self.marker_overlay = MarkerOverlay()
        self.marker_overlay.setParent(self)
        self.marker_overlay.setFixedSize(screen_size)

        self.keyboard = Keyboard()
        self.keyboard.setParent(self)
        self.keyboard.setFixedSize(screen_size.width(), screen_size.height() * 0.5)
        self.keyboard.move(0, self.height() - self.keyboard.height())

        self.gaze_overlay = GazeOverlay()
        self.gaze_overlay.setParent(self)
        self.gaze_overlay.setFixedSize(screen_size)

    def update_data(self, eye_tracking_data):
        if eye_tracking_data.gaze is not None:
            gaze = QPoint(*eye_tracking_data.gaze)
            self.gaze_overlay.update_data(gaze, eye_tracking_data.dwell_process)
            self.marker_overlay.update_data(eye_tracking_data.detected_markers)

    def resizeEvent(self, event: QResizeEvent) -> None:
        pass

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()
        return super().keyReleaseEvent(event)
