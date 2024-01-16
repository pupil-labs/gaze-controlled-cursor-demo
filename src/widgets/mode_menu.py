from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import *
from PySide6.QtMultimedia import QSoundEffect


class ModeMenu(QWidget):
    mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.buttons = []

        btn = MenuButton("View")
        btn.clicked.connect(lambda: self.mode_changed.emit("View"))
        layout.addWidget(btn)
        self.buttons.append(btn)

        btn = MenuButton("Click")
        btn.clicked.connect(lambda: self.mode_changed.emit("Click"))
        layout.addWidget(btn)
        self.buttons.append(btn)

        btn = MenuButton("Zoom")
        btn.clicked.connect(lambda: self.mode_changed.emit("Zoom"))
        layout.addWidget(btn)
        self.buttons.append(btn)

        btn = MenuButton("Keyboard")
        btn.clicked.connect(lambda: self.mode_changed.emit("Keyboard"))
        layout.addWidget(btn)
        self.buttons.append(btn)

        self.setLayout(layout)

        self.setVisible(False)

    def update_data(self, gaze: QPoint):
        if self.isVisible():
            for btn in self.buttons:
                if btn.check_press(gaze):
                    self.setVisible(False)

    def resizeEvent(self, event: QResizeEvent) -> None:
        return super().resizeEvent(event)


class MenuButton(QPushButton):
    def __init__(self, label, code=None):
        self.code = code
        if code is None:
            self.code = label
        super().__init__(label)
        self.setStyleSheet(
            "background-color: gray; margin:0; border: 1px solid black; padding:0; color: black; border-radius: 10px; font-size: 20px;"
        )
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.key_sound = QSoundEffect()
        self.key_sound.setSource(QUrl.fromLocalFile("key-stroke.wav"))

    def check_press(self, point):
        point = self.mapFromGlobal(point)
        if self.rect().contains(point):
            self.key_sound.play()
            self.clicked.emit()
            return True
        return False
