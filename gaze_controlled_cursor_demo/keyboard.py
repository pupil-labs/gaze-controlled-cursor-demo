from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent, QResizeEvent
from PySide6.QtWidgets import *


class Keyboard(QWidget):
    keyPressed = Signal(str)

    def __init__(self):
        super().__init__()
        self.enabled = True

        layout = QGridLayout()

        for i in range(20):
            layout.setColumnStretch(i, 1)
        for i in range(8):
            layout.setRowStretch(i, 1)

        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        qwerty_keys = "QWERTYUIOPASDFGHJKLZXCVBNM"

        row_idx = 0
        col_idx = 0
        self.keys = []
        for idx, key in enumerate(qwerty_keys):
            if idx in [10, 19]:
                row_idx += 1
                col_idx = 0
            k = Key(key)
            self.keys.append(k)
            layout.addWidget(k, row_idx * 2, col_idx * 2 + row_idx, 2, 2)
            col_idx += 1

        k = Key(" ", label="SPACE")
        self.keys.append(k)
        layout.addWidget(k, 6, 2, 2, 6)

        k = Key("backspace", label="backspace")
        self.keys.append(k)
        layout.addWidget(k, 6, 8, 2, 4)

        k = Key("enter", label="enter")
        self.keys.append(k)
        layout.addWidget(k, 6, 12, 2, 4)

        k = Key("keyboard_toggle", label="keys")
        self.keys.append(k)
        layout.addWidget(k, 6, 16, 2, 2)

        self.setLayout(layout)

        op = QGraphicsOpacityEffect(self)
        op.setOpacity(0.5)  # 0 to 1 will cause the fade effect to kick in
        self.setGraphicsEffect(op)
        self.setAutoFillBackground(True)

    def toggleKeyboard(self):
        self.enabled = not self.enabled
        for key in self.keys:
            if key.key != "keyboard_toggle":
                key.setVisible(not key.isVisible())

    def paintEvent(self, event):
        pass

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        pass

    def intersect(self, gaze_location):
        for key in self.keys:
            if key.isVisible():
                p = key.mapFromGlobal(gaze_location)
                if key.rect().contains(p):
                    self.keyPressed.emit(key.key)

    def isInside(self, gaze_location):
        p = self.mapFromGlobal(gaze_location)
        return self.rect().contains(p)


class Key(QPushButton):
    def __init__(self, key, label=None, signal=None):
        if label is None:
            label = key
        super().__init__(label)
        self.key = key
        self.signal = signal
        self.setStyleSheet(
            "background-color: white; margin:0; border: 1px solid black; padding:0; color: black; border-radius: 10px; font-size: 20px;"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.connect(self, SIGNAL("clicked()"), self.clicked)

    # def clicked(self):
    #     if self.signal is not None:
    #         self.signal.emit()
    #     else:
    #         pyautogui.keyDown(self.key)

    #     pygame.mixer.Sound.play(key_sound)

    def resizeEvent(self, event: QResizeEvent) -> None:
        return super().resizeEvent(event)
