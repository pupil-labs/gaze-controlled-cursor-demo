from PySide6.QtCore import *
from PySide6.QtGui import *
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
        if self.gaze is None:
            return

        render_point = self.mapFromGlobal(self.gaze)
        with QPainter(self) as painter:
            red = QColor(Qt.red)
            red.setAlphaF(0.3)
            painter.setBrush(red)
            painter.drawEllipse(
                render_point,
                self.gaze_circle_radius,
                self.gaze_circle_radius,
            )

            green = QColor(Qt.green)
            green.setAlphaF(0.3)
            painter.setBrush(green)
            painter.drawEllipse(
                render_point,
                self.gaze_circle_radius * self.dwell_process,
                self.gaze_circle_radius * self.dwell_process,
            )
