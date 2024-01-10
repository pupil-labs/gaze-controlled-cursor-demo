import os
import numpy as np

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent, QResizeEvent
from PySide6.QtWidgets import *

from widgets.marker_overlay import MarkerOverlay
from widgets.gaze_overlay import GazeOverlay
from widgets.keyboard import Keyboard


class MainWindow(QWidget):
    surface_changed = Signal()

    def __init__(self):
        super().__init__()

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")

        # Make window transparent for mouse events such that any click will be passed through to the window below.
        self.setWindowFlag(Qt.WindowTransparentForInput)

        self.marker_overlay = MarkerOverlay()
        self.marker_overlay.setParent(self)

        self.keyboard = Keyboard()
        self.keyboard.setParent(self)

        self.gaze_overlay = GazeOverlay()
        self.gaze_overlay.setParent(self)

    def update_data(self, eye_tracking_data):
        if eye_tracking_data.gaze is not None:
            gaze = QPoint(*eye_tracking_data.gaze)
            self.gaze_overlay.update_data(gaze, eye_tracking_data.dwell_process)
            self.marker_overlay.update_data(eye_tracking_data.detected_markers)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.marker_overlay.resize(self.size())
        self.gaze_overlay.resize(self.size())
        self.keyboard.resize(self.width(), self.height() * 0.5)
        self.keyboard.move(0, self.height() - self.keyboard.height())

    def moveEvent(self, event):
        self.surface_changed.emit()

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()
        return super().keyReleaseEvent(event)
