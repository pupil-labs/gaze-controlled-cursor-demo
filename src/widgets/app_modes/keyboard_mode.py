from .app_mode import AppMode

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from eye_tracking_provider import EyeTrackingData

from widgets.gaze_button import GazeButton
from gaze_event_type import GazeEventType
import actions


class KeyboardMode(AppMode):
    def __init__(self, parent=None, event_handlers=None):
        super().__init__(parent, event_handlers)

        self.keyboard = Keyboard(self)
        self.keyboard.keyPressed.connect(event_handlers["on_key_pressed"])

    def _update_data(self, eye_tracking_data: EyeTrackingData):
        self.keyboard.update_data(eye_tracking_data)

    def resize(self, size):
        super().resize(size)
        height_ratio = 0.55
        self.keyboard.setGeometry(
            0,
            size.height() * (1 - height_ratio),
            size.width(),
            size.height() * height_ratio,
        )


class Keyboard(QWidget):
    keyPressed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.caps = False
        self.qwerty_keys = "qwertyuiopasdfghjklzxcvbnm"

        layout = QGridLayout()

        for i in range(20):
            layout.setColumnStretch(i, 1)
        for i in range(6):
            layout.setRowStretch(i, 1)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self._add_basic_keys(layout)
        self.setLayout(layout)

        for key in self.keys:
            if key.code == "CAPS":
                key.clicked.connect(self._toggle_caps)
            else:
                key.clicked.connect(lambda v: self.keyPressed.emit(v))

        edge_action_configs = []

        a_config = actions.EdgeActionConfig()
        a = actions.KeyPressAction(" ")
        a_config.action = a
        a_config.event = GazeEventType.FIXATE
        a_config.screen_edge = actions.ScreenEdge.BOTTOM_MIDDLE
        edge_action_configs.append(a_config)
        a.key_pressed.connect(lambda v: self.keyPressed.emit(v))

        a_config = actions.EdgeActionConfig()
        a = actions.KeyPressAction("backspace")
        a_config.action = a
        a_config.event = GazeEventType.FIXATE
        a_config.screen_edge = actions.ScreenEdge.BOTTOM_LEFT
        edge_action_configs.append(a_config)
        a.key_pressed.connect(lambda v: self.keyPressed.emit(v))

        a_config = actions.EdgeActionConfig()
        a = actions.KeyPressAction("enter")
        a_config.action = a
        a_config.event = GazeEventType.FIXATE
        a_config.screen_edge = actions.ScreenEdge.BOTTOM_RIGHT
        edge_action_configs.append(a_config)
        a.key_pressed.connect(lambda v: self.keyPressed.emit(v))

        self.edge_action_handler = actions.EdgeActionHandler(
            QApplication.primaryScreen(), edge_action_configs
        )

        op = QGraphicsOpacityEffect(self)
        op.setOpacity(0.5)
        self.setGraphicsEffect(op)
        self.setAutoFillBackground(True)

    def _add_basic_keys(self, layout):
        row_idx = 0
        col_idx = 0
        self.keys = []
        for idx, key in enumerate(self.qwerty_keys):
            if idx in [10, 19]:
                row_idx += 1
                col_idx = 0
            k = Key(key)
            self.keys.append(k)
            layout.addWidget(k, row_idx * 2, col_idx * 2 + row_idx, 2, 2)
            col_idx += 1

    def update_data(self, eye_tracking_data):
        if eye_tracking_data.gaze is None:
            return

        for key in self.keys:
            key.update_data(eye_tracking_data)

        self.edge_action_handler.update_data(eye_tracking_data)

    def _toggle_caps(self):
        self.caps = not self.caps

        for key in self.keys:
            if key.code.isalpha() and len(key.code) == 1:
                key.toggleCaps()


class Key(GazeButton):
    def toggleCaps(self):
        if self.text().isupper():
            self.setText(self.text().lower())
            self.code = self.code.lower()
        else:
            self.setText(self.text().upper())
            self.code = self.code.upper()
