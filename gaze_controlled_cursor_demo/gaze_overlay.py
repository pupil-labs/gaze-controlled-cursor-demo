from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent, QResizeEvent
from PySide6.QtWidgets import *


class GazeOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.gaze_circle_radius = 20.0
        self.gaze = None
        self.dwell_process = 0.0

    def update_data(self, gaze, dwell_process):
        self.gaze = gaze
        self.dwell_process = dwell_process
        self.update()

    def paintEvent(self, event):
        with QPainter(self) as painter:
            if self.gaze is not None:
                red = QColor(Qt.red)
                red.setAlphaF(0.3)
                painter.setBrush(red)
                painter.drawEllipse(
                    self.gaze,
                    self.gaze_circle_radius,
                    self.gaze_circle_radius,
                )
                green = QColor(Qt.green)
                green.setAlphaF(0.3)
                painter.setBrush(green)
                painter.drawEllipse(
                    self.gaze,
                    self.gaze_circle_radius * self.dwell_process,
                    self.gaze_circle_radius * self.dwell_process,
                )
