from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import *
import pyautogui
import pygame


class Keyboard(QWidget):
    def __init__(self):
        super().__init__()
        layout = QGridLayout()
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
            layout.addWidget(k, row_idx, col_idx * 2 + row_idx, 1, 2)
            col_idx += 1

        k = Key(" ", label="SPACE")
        self.keys.append(k)
        layout.addWidget(k, 3, 2, 1, 7)

        k = Key("backspace", label="backspace")
        self.keys.append(k)
        layout.addWidget(k, 3, 9, 1, 4)

        k = Key("enter", label="enter")
        self.keys.append(k)
        layout.addWidget(k, 3, 13, 1, 4)

        self.setLayout(layout)
        self.setFixedSize(2560, 768)

        op = QGraphicsOpacityEffect(self)
        op.setOpacity(0.5)  # 0 to 1 will cause the fade effect to kick in
        self.setGraphicsEffect(op)
        # self.setAutoFillBackground(True)

    def paintEvent(self, event):
        pass

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        pass

    def intersect(self, gaze_location):
        for key in self.keys:
            p = key.mapFromGlobal(gaze_location)
            if key.rect().contains(p):
                key.clicked()
                break


pygame.init()
key_sound = pygame.mixer.Sound("key-stroke.mp3")


class Key(QPushButton):
    def __init__(self, key, label=None):
        if label is None:
            label = key
        super().__init__(label)
        self.key = key
        self.setStyleSheet(
            "background-color: white; margin:0; border: 1px solid black; padding:0; color: black; border-radius: 10px; font-size: 20px;"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.connect(self, SIGNAL("clicked()"), self.clicked)

    def clicked(self):
        pyautogui.keyDown(self.key)
        pygame.mixer.Sound.play(key_sound)
        print(self.text())
