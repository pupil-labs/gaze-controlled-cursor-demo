from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtMultimedia import QSoundEffect

from eye_tracking_provider import EyeTrackingData


class ButtonStyle:
    def __init__(self, background_color="white", color="black", font_size=35):
        self.background_color = background_color
        self.color = color
        self.font_size = font_size

    def to_css(self):
        return f"background-color: {self.background_color}; margin:0; border: 1px solid black; padding:0; color: {self.color}; border-radius: 10px; font-size: {self.font_size}px; font-weight: 900;"


class GazeButton(QPushButton):
    clicked = Signal(str)

    def __init__(
        self, label, code=None, regular_style=ButtonStyle(), hover_style=ButtonStyle()
    ):
        self.code = code
        if code is None:
            self.code = label
        super().__init__(label)

        self.regular_style = regular_style
        self.hover_style = hover_style
        self.dwell_process = 0.0
        self.hover = False

        self.setStyleSheet(regular_style.to_css())
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.key_sound = QSoundEffect()
        self.key_sound.setSource(QUrl.fromLocalFile("key-stroke.wav"))

    def update_data(self, eye_tracking_data: EyeTrackingData):
        if not self.isVisible():
            return

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

        if not self.isVisible():
            return

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
            self.setStyleSheet(self.hover_style.to_css())
        else:
            self.hover = False
            self.setStyleSheet(self.regular_style.to_css())
