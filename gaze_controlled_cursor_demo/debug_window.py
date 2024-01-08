import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent, QResizeEvent
from PySide6.QtWidgets import *


class DebugWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)
        layout = QVBoxLayout()

        self.img_label = QLabel()
        self.img_label.setText("")
        self.img_label.setScaledContents(True)
        self.img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout.addWidget(self.img_label)

        # self.img_label.setAlignment(Qt.AlignCenter)
        # self.img_label.setStyleSheet("background:transparent;")

        self.setLayout(layout)

    def update(self, data):
        scene = data.scene.bgr_pixels
        height, width, _ = scene.shape
        bytesPerLine = 3 * width
        qImg = QImage(scene.data, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap(qImg)
        self.img_label.setPixmap(pixmap)
        # self.img_label.resize(pixmap.width(), pixmap.height())
        # self.resize(pixmap.width(), pixmap.height())

    def paintEvent(self, event):
        pass

    def resizeEvent(self, event: QResizeEvent) -> None:
        pass
