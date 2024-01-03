import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import *

from eye_tracking_provider import Marker
from keyboard import Keyboard


class MainWindow(QWidget):
    def __init__(self, screen_size):
        super().__init__()
        self.gaze_location = None
        self.gaze_circle_radius = 20.0
        self.dwell_process = None

        self.setFixedSize(screen_size)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")

        # Make window transparent for mouse events such that any click will be passed through to the window below.
        # self.setWindowFlag(Qt.WindowTransparentForInput)

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

        self.keyboard = Keyboard()
        self.keyboard.setParent(self)
        # self.keyboard.setFixedSize(screen_size.width(), screen_size.width() / 10 * 4)
        self.keyboard.setFixedSize(screen_size.width(), screen_size.width() / 10 * 3)
        self.keyboard.move(0, self.height() - self.keyboard.height())

    def update_gaze(self, gaze, dwell_process):
        if gaze is None:
            self.gaze_location = None
            self.dwell_process = None
        else:
            self.gaze_location = self.mapFromGlobal(QPoint(*gaze))
            self.dwell_process = dwell_process

        if dwell_process >= 1.0:
            self.keyboard.intersect(self.gaze_location)

        self.repaint()

    def paintEvent(self, event):
        with QPainter(self) as painter:
            painter = QPainter(self)

            if self.gaze_location is not None:
                painter.setBrush(Qt.red)
                painter.drawEllipse(
                    self.gaze_location,
                    self.gaze_circle_radius,
                    self.gaze_circle_radius,
                )

                painter.setBrush(Qt.green)
                painter.drawEllipse(
                    self.gaze_location,
                    self.gaze_circle_radius * self.dwell_process,
                    self.gaze_circle_radius * self.dwell_process,
                )

        self.updateMask()

    def updateMask(self):
        mask = QRegion(0, 0, 0, 0)
        for marker in self.markers:
            mask = mask.united(marker.geometry())
        mask = mask.united(self.keyboard.geometry())

        # if self.gaze_location is not None:
        #     rect = QRect(
        #         self.gaze_location.x() - self.gaze_circle_radius,
        #         self.gaze_location.y() - self.gaze_circle_radius,
        #         self.gaze_circle_radius * 2,
        #         self.gaze_circle_radius * 2,
        #     )
        #     mask = mask.united(rect)

        self.setMask(mask)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()
        return super().keyReleaseEvent(event)
