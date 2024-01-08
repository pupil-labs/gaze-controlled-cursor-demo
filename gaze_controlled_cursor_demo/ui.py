import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent, QResizeEvent
from PySide6.QtWidgets import *

from eye_tracking_provider import Marker
from gaze_overlay import GazeOverlay
from keyboard import Keyboard
import utils


class MainWindow(QWidget):
    surface_changed = Signal()

    def __init__(self, screen_size):
        super().__init__()

        self.setFixedSize(screen_size)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background:transparent;")

        # Make window transparent for mouse events such that any click will be passed through to the window below.
        self.setWindowFlag(Qt.WindowTransparentForInput)

        layout = QGridLayout()
        for i in range(20):
            layout.setColumnStretch(i, 1)
        for i in range(16):
            layout.setRowStretch(i, 1)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.markers = []
        # for i in range(20):
        #     for j in range(16):
        #         m = Marker(i * 20 + j, Qt.AlignLeft | Qt.AlignTop)
        #         layout.addWidget(m, j, i, 1, 1)
        #         self.markers.append(m)

        m = Marker(0, Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(m, 0, 0, 3, 2)
        self.markers.append(m)

        m = Marker(1, Qt.AlignLeft | Qt.AlignBottom)
        layout.addWidget(m, 13, 0, 3, 2)
        self.markers.append(m)

        m = Marker(2, Qt.AlignRight | Qt.AlignTop)
        layout.addWidget(m, 0, 18, 3, 2)
        self.markers.append(m)

        m = Marker(3, Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(m, 13, 18, 3, 2)
        self.markers.append(m)

        self.setLayout(layout)

        self.keyboard = Keyboard()
        self.keyboard.setParent(self)
        self.keyboard.setFixedSize(screen_size.width(), screen_size.height() * 0.5)
        self.keyboard.move(0, self.height() - self.keyboard.height())

        self.gaze_overlay = GazeOverlay()
        self.gaze_overlay.setParent(self)
        self.gaze_overlay.setFixedSize(screen_size)

        self.updateMask()

    def update(self, gaze, dwell_process):
        if gaze is None:
            self.gaze_location = None
            self.dwell_process = None
        else:
            gaze = self.mapFromGlobal(QPoint(*gaze))
            dwell_process = dwell_process

            self.gaze_overlay.update(gaze, dwell_process)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.updateMask()
        self.surface_changed.emit()
        return super().resizeEvent(event)

    def updateMask(self):
        mask = QRegion(0, 0, 0, 0)
        for marker in self.markers:
            mask = mask.united(utils.map_rect_to_global(marker))

        mask = mask.united(self.keyboard.geometry())

        # self.setMask(mask)

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key_Escape:
            self.close()
        return super().keyReleaseEvent(event)
