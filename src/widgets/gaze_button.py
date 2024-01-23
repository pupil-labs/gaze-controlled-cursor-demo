from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtMultimedia import QSoundEffect

from eye_tracking_provider import EyeTrackingData


class GazeButton(QPushButton):
    clicked = Signal(str)

    def __init__(self, label, code=None):
        self.code = code
        if code is None:
            self.code = label
        super().__init__(label)

        self.dwell_process = 0.0
        self.hover = False

        self.setStyleSheet(
            "background-color: white; margin:0; border: 1px solid black; padding:0; color: black; border-radius: 10px; font-size: 20px;"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.key_sound = QSoundEffect()
        self.key_sound.setSource(QUrl.fromLocalFile("key-stroke.wav"))

    def update_data(self, eye_tracking_data: EyeTrackingData):
        p = QPoint(*eye_tracking_data.gaze)
        p = self.mapFromGlobal(p)
        if self.rect().contains(p):
            self.set_hover(True)
            self.dwell_process = eye_tracking_data.dwell_process
            if eye_tracking_data.dwell_process == 1.0:
                self.key_sound.play()
                self.clicked.emit(self.code)
        else:
            self.set_hover(False)
            self.dwell_process = 0.0

    def paintEvent(self, event):
        super().paintEvent(event)

        if self.dwell_process > 0.0:
            with QPainter(self) as painter:
                color = QColor(Qt.white)
                color.setAlpha(0.5)
                painter.setBrush(color)
                center = self.rect().center()
                size = self.rect().size() * self.dwell_process / 2
                painter.drawEllipse(center, size.width(), size.height())

    def set_hover(self, highlight):
        if highlight:
            self.hover = True
            self.setStyleSheet(
                "background-color: white; margin:0; border: 1px solid black; padding:0; color: black; border-radius: 10px; font-size: 20px;"
            )
        else:
            self.hover = False
            self.setStyleSheet(
                "background-color: #b3b3b3; margin:0; border: 1px solid black; padding:0; color: black; border-radius: 10px; font-size: 20px;"
            )
