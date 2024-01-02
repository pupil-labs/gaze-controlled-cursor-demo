import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from gaze_provider import GazeProvider


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayout(QGridLayout())
        self.gaze_location = None
        self.gaze_circle_radius = 10.0

    def update_gaze(self, gaze):
        if gaze is None:
            self.gaze_location = None
        else:
            self.gaze_location = self.mapFromGlobal(gaze)
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(Qt.red)

        if self.gaze_location is not None:
            painter.drawEllipse(
                self.gaze_location,
                self.gaze_circle_radius,
                self.gaze_circle_radius,
            )
