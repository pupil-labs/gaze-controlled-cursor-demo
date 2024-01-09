from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent, QResizeEvent
from PySide6.QtWidgets import *

from widgets.marker_overlay import MarkerOverlay
from widgets.gaze_overlay import GazeOverlay
from widgets.keyboard import Keyboard


class MainWindow(QWidget):
    key_pressed = Signal(QKeyEvent)

    def __init__(self, screen_size):
        super().__init__()
        self.target_location = None
        self.target_color = None
        self.target_radius = 10

        self.setFixedSize(screen_size)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setStyleSheet("background:gray;")

        self.marker_overlay = MarkerOverlay()
        self.marker_overlay.setParent(self)
        self.marker_overlay.setFixedSize(screen_size)

        self.gaze_overlay = GazeOverlay()
        self.gaze_overlay.setParent(self)
        self.gaze_overlay.setFixedSize(screen_size)

        self.time = None

    def update_data(self, eye_tracking_data, target_location, target_color):
        self.target_location = target_location
        self.target_color = target_color

        if eye_tracking_data is not None and eye_tracking_data.gaze is not None:
            gaze = QPoint(*eye_tracking_data.gaze)
            # self.gaze_overlay.update_data(gaze, eye_tracking_data.dwell_process)
            self.marker_overlay.update_data(eye_tracking_data.detected_markers)

        self.update()

    def paintEvent(self, event):
        with QPainter(self) as painter:
            if self.target_location is not None:
                painter.setBrush(self.target_color)
                painter.drawEllipse(
                    self.target_location,
                    self.target_radius,
                    self.target_radius,
                )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Return:
            self.key_pressed.emit(event)
        else:
            super().keyPressEvent(event)
