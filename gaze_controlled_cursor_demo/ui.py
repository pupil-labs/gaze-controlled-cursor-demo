import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import *

from gaze_provider import Marker


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.gaze_location = None
        self.gaze_circle_radius = 10.0

        self.showMaximized()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.markers = [Marker(i) for i in range(4)]
        coordinates = [
            (0, 0),
            (self.width() - self.markers[1].width(), 0),
            (0, self.height() - self.markers[2].height()),
            (
                self.width() - self.markers[3].width(),
                self.height() - self.markers[3].height(),
            ),
        ]
        for marker, coords in zip(self.markers, coordinates):
            marker.setParent(self)
            marker.move(*coords)

    def update_gaze(self, gaze):
        if gaze is None:
            self.gaze_location = None
        else:
            self.gaze_location = self.mapFromGlobal(QPoint(*gaze))
        self.repaint()

    def paintEvent(self, event):
        with QPainter(self) as painter:
            painter = QPainter(self)
            painter.setBrush(Qt.red)

            if self.gaze_location is not None:
                painter.drawEllipse(
                    self.gaze_location,
                    self.gaze_circle_radius,
                    self.gaze_circle_radius,
                )

        # self.updateMask()

    def updateMask(self):
        mask = QRegion(0, 0, 0, 0)
        for marker in self.markers:
            rect = QRect(marker.pos(), marker.size())
            mask = mask.united(rect)

        if self.gaze_location is not None:
            rect = QRect(
                self.gaze_location.x() - self.gaze_circle_radius,
                self.gaze_location.y() - self.gaze_circle_radius,
                self.gaze_circle_radius * 2,
                self.gaze_circle_radius * 2,
            )
            mask = mask.united(rect)
        self.setMask(mask)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()
        return super().keyReleaseEvent(event)
