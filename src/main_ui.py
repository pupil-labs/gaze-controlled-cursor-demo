import os
import numpy as np

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent, QResizeEvent
from PySide6.QtWidgets import *

from widgets.marker_overlay import MarkerOverlay
from widgets.gaze_overlay import GazeOverlay
from widgets.keyboard import Keyboard
from widgets.selection_zoom import SelectionZoom


class MainWindow(QWidget):
    surface_changed = Signal()
    hidden = Signal()

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

        self.selection_zoom = SelectionZoom()

        self.keyboard = Keyboard()
        self.keyboard.setParent(self)

        self.gaze_overlay = GazeOverlay()
        self.gaze_overlay.setParent(self)
        self.gaze_overlay.setGeometry(self.screen().geometry())

        self.measuring = True
        self.showMaximized()

    def paintEvent(self, event):
        if self.measuring:
            tl = self.mapToGlobal(QPoint(0, 0))
            br = self.mapToGlobal(QPoint(self.size().width(), self.size().height()))
            self.desktop_geometry = QRect(tl, br)
            self.measuring = False
            self.marker_overlay.setGeometry(self.desktop_geometry)
            self.keyboard.setGeometry(QRect(
                self.desktop_geometry.left(),
                self.desktop_geometry.height()/2,
                self.desktop_geometry.width(),
                self.desktop_geometry.height()/2
            ))

            QTimer.singleShot(1, self.hide)
            return

    def render_as_overlay(self, painter):
        self.render(painter, self.mapToGlobal(self.geometry().topLeft()))
        overlay_widget_global_pos = self.gaze_overlay.mapToGlobal(self.gaze_overlay.geometry().topLeft())
        self.gaze_overlay.render(painter, overlay_widget_global_pos)

    def update_data(self, eye_tracking_data):
        if eye_tracking_data.gaze is not None:
            gaze = QPoint(*eye_tracking_data.gaze)
            self.gaze_overlay.update_data(gaze, eye_tracking_data.dwell_process)

    def moveEvent(self, event):
        self.surface_changed.emit()

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()
        return super().keyReleaseEvent(event)
