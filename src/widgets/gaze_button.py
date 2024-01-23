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
            self.set_highlight(True)
            if eye_tracking_data.dwell_process == 1.0:
                self.key_sound.play()
                self.clicked.emit(self.code)
        else:
            self.set_highlight(False)

    def set_highlight(self, highlight):
        if highlight:
            self.setStyleSheet(
                "background-color: white; margin:0; border: 1px solid black; padding:0; color: black; border-radius: 10px; font-size: 20px;"
            )
        else:
            self.setStyleSheet(
                "background-color: #b3b3b3; margin:0; border: 1px solid black; padding:0; color: black; border-radius: 10px; font-size: 20px;"
            )
