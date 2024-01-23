import itertools
from .app_mode import AppMode

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from eye_tracking_provider import EyeTrackingData

from widgets.gaze_button import GazeButton, ButtonStyle
from gaze_event_type import GazeEventType
import actions

from enum import Enum


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


class Page(Enum):
    LETTERS = 0
    CAPS = 1
    SPECIAL = 2


class Keyboard(QWidget):
    keyPressed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.caps = False

        layout = QGridLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        for i in range(20):
            layout.setColumnStretch(i, 1)
        for i in range(6):
            layout.setRowStretch(i, 1)

        self.pages = {}
        self.pages[Page.LETTERS] = self._generate_letters_page(layout)
        self.pages[Page.CAPS] = self._generate_letters_page(layout, caps=True)
        self.pages[Page.SPECIAL] = self._generate_special_page(layout)
        self._set_page(Page.LETTERS)

        self.keys = list(itertools.chain.from_iterable(self.pages.values()))

        self.setLayout(layout)

        self._setup_edge_actions()

        op = QGraphicsOpacityEffect(self)
        op.setOpacity(0.6)
        self.setGraphicsEffect(op)
        self.setAutoFillBackground(True)

    def _generate_letters_page(self, layout, caps=False):
        qwerty_keys = "qwertyuiopasdfghjklzxcvbnm"
        if caps:
            qwerty_keys = qwerty_keys.upper()

        if caps:
            regular_style = ButtonStyle(background_color="#FFCCCB")
            hover_style = ButtonStyle(background_color="white")
        else:
            regular_style = ButtonStyle()
            hover_style = ButtonStyle(background_color="lightgray")

        row_idx = 0
        col_idx = 0
        keys = []
        for idx, key in enumerate(qwerty_keys):
            if idx in [10, 19]:
                row_idx += 1
                col_idx = 0
            k = Key(key, regular_style=regular_style, hover_style=hover_style)
            keys.append(k)
            layout.addWidget(k, row_idx * 2, col_idx * 2 + row_idx, 2, 2)
            col_idx += 1

        k = Key("Space", " ", regular_style=regular_style, hover_style=hover_style)
        keys.append(k)
        layout.addWidget(k, 4, 16, 2, 2)

        for key in keys:
            key.clicked.connect(lambda v: self.keyPressed.emit(v))

        return keys

    def _generate_special_page(self, layout):
        special_chars = "1234567890-=!@#$%^*()_+,."
        regular_style = ButtonStyle(background_color="lightblue")
        hover_style = ButtonStyle(background_color="white")

        keys = []
        row_idx = 0
        col_idx = 0
        keys = []
        for idx, key in enumerate(special_chars):
            if idx in [10, 19]:
                row_idx += 1
                col_idx = 0
            k = Key(key, regular_style=regular_style, hover_style=hover_style)
            keys.append(k)
            layout.addWidget(k, row_idx * 2, col_idx * 2 + row_idx, 2, 2)
            col_idx += 1

        k = Key(
            "Backspace",
            "backspace",
            regular_style=regular_style,
            hover_style=hover_style,
        )
        keys.append(k)
        layout.addWidget(k, 4, 16, 2, 2)

        for key in keys:
            key.clicked.connect(lambda v: self.keyPressed.emit(v))

        return keys

    def _setup_edge_actions(self):
        edge_action_configs = []

        a_config = actions.EdgeActionConfig()
        a = actions.KeyPressAction("page")
        a_config.action = a
        a_config.event = GazeEventType.GAZE_ENTER
        a_config.screen_edge = actions.ScreenEdge.RIGHT_BOTTOM
        edge_action_configs.append(a_config)
        a.key_pressed.connect(self._toggle_special)

        a_config = actions.EdgeActionConfig()
        a = actions.KeyPressAction("caps")
        a_config.action = a
        a_config.event = GazeEventType.GAZE_ENTER
        a_config.screen_edge = actions.ScreenEdge.LEFT_BOTTOM
        edge_action_configs.append(a_config)
        a.key_pressed.connect(self._toggle_caps)

        self.edge_action_handler = actions.EdgeActionHandler(
            QApplication.primaryScreen(), edge_action_configs
        )

    def _set_page(self, value: Page):
        self.current_page = value
        for page, keys in self.pages.items():
            if page == value:
                for key in keys:
                    key.setVisible(True)
            else:
                for key in keys:
                    key.setVisible(False)

    def update_data(self, eye_tracking_data):
        if eye_tracking_data.gaze is None:
            return

        for key in self.keys:
            key.update_data(eye_tracking_data)

        self.edge_action_handler.update_data(eye_tracking_data)

    def _toggle_caps(self):
        if self.current_page == Page.CAPS:
            self._set_page(Page.LETTERS)
        else:
            self._set_page(Page.CAPS)

    def _toggle_special(self):
        if self.current_page == Page.SPECIAL:
            self._set_page(Page.LETTERS)
        else:
            self._set_page(Page.SPECIAL)


class Key(GazeButton):
    def toggleCaps(self):
        if self.text().isupper():
            self.setText(self.text().lower())
            self.code = self.code.lower()
        else:
            self.setText(self.text().upper())
            self.code = self.code.upper()
