import time

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import *
from PySide6.QtMultimedia import QSoundEffect

from eye_tracking_provider import EyeTrackingData
from widgets.gaze_button import GazeButton


class ModeMenu(QWidget):
    mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.disappear_timeout = 3.0
        self.lost_focus_at = None

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.buttons = []

        btn = GazeButton("View")
        btn.clicked.connect(lambda: self.mode_changed.emit("View"))
        layout.addWidget(btn)
        self.buttons.append(btn)

        btn = GazeButton("Click")
        btn.clicked.connect(lambda: self.mode_changed.emit("Click"))
        layout.addWidget(btn)
        self.buttons.append(btn)

        btn = GazeButton("Zoom")
        btn.clicked.connect(lambda: self.mode_changed.emit("Zoom"))
        layout.addWidget(btn)
        self.buttons.append(btn)

        btn = GazeButton("Keyboard")
        btn.clicked.connect(lambda: self.mode_changed.emit("Keyboard"))
        layout.addWidget(btn)
        self.buttons.append(btn)

        self.setLayout(layout)

        self.mode_change = False
        for btn in self.buttons:
            btn.clicked.connect(self.on_button_clicked)

        op = QGraphicsOpacityEffect(self)
        op.setOpacity(0.5)
        self.setGraphicsEffect(op)
        self.setAutoFillBackground(True)

        self.setVisible(False)

    def on_button_clicked(self):
        self.setVisible(False)
        self.mode_change = True

    def update_data(self, eye_tracking_data: EyeTrackingData):
        if eye_tracking_data is None:
            return

        self.mode_change = False
        if self.isVisible():
            if eye_tracking_data.gaze is None:
                return

            for btn in self.buttons:
                btn.update_data(eye_tracking_data)

            gaze = QPoint(*eye_tracking_data.gaze)
            p = self.mapFromGlobal(gaze)
            if self.rect().contains(p):
                self.lost_focus_at = None
            else:
                if self.lost_focus_at is None:
                    self.lost_focus_at = time.time()
                else:
                    if time.time() - self.lost_focus_at > self.disappear_timeout:
                        self.setVisible(False)
                        self.lost_focus_at = None
