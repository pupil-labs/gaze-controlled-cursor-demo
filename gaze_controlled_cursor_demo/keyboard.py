from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent, QResizeEvent
from PySide6.QtWidgets import *


class Keyboard(QWidget):
    keyPressed = Signal(str)

    def __init__(self):
        super().__init__()
        self.enabled = True
        self.qwerty_keys = "QWERTYUIOPASDFGHJKLZXCVBNM"

        layout = QGridLayout()

        for i in range(20):
            layout.setColumnStretch(i, 1)
        for i in range(8):
            layout.setRowStretch(i, 1)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        self._add_basic_keys(layout)
        self._add_special_keys(layout)
        self.setLayout(layout)

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

    def _add_special_keys(self, layout):
        # k = Key("CAPS", code="CAPS")
        # self.keys.append(k)
        # layout.addWidget(k, 6, 2, 2, 6)

        k = Key("SPACE", code=" ")
        self.keys.append(k)
        layout.addWidget(k, 6, 2, 2, 6)

        k = Key("backspace", code="backspace")
        self.keys.append(k)
        layout.addWidget(k, 6, 8, 2, 4)

        k = Key("enter", code="enter")
        self.keys.append(k)
        layout.addWidget(k, 6, 12, 2, 4)

        k = Key("keys", code="keyboard_toggle")
        self.keys.append(k)
        layout.addWidget(k, 6, 16, 2, 2)

    def toggleKeyboard(self):
        self.enabled = not self.enabled
        for key in self.keys:
            if key.key != "keyboard_toggle":
                key.setVisible(not key.isVisible())

    def update_data(self, gaze):
        gaze = QPoint(*gaze)
        for key in self.keys:
            if self.enabled:
                p = key.mapFromGlobal(gaze)
                if key.rect().contains(p):
                    if key.code in self.qwerty_keys:
                        self.keyPressed.emit(key.code)
                    else:
                        if key.code == "keyboard_toggle":
                            self.toggleKeyboard()


class Key(QPushButton):
    def __init__(self, label, code=None):
        self.code = code
        if code is None:
            self.code = label
        super().__init__(label)
        self.setStyleSheet(
            "background-color: white; margin:0; border: 1px solid black; padding:0; color: black; border-radius: 10px; font-size: 20px;"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def resizeEvent(self, event: QResizeEvent) -> None:
        return super().resizeEvent(event)
