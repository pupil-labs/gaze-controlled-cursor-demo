from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import pyautogui
from PIL.ImageQt import ImageQt


class SelectionZoom(QLabel):
    click_made = Signal(QPoint)

    def __init__(self, screen_size):
        super().__init__()
        self.crop_size = screen_size * 0.2
        self.zoom_factor = 3
        self.zoom_size = self.crop_size * self.zoom_factor
        self.crop_offset = QPoint(
            QPoint((self.crop_size * 0.5).width(), (self.crop_size * 0.5).height())
        )
        self.zoom_offset = QPoint(
            QPoint((self.zoom_size * 0.5).width(), (self.zoom_size * 0.5).height())
        )

        self.setFixedSize(self.zoom_size)
        self.setVisible(False)

    def update_data(self, pos):
        pos = QPoint(*pos)

        if not self.isVisible():
            self.enable(pos)
        else:
            pos_local = self.mapFromGlobal(pos)
            if self.rect().contains(pos_local):
                # pos_local = pos_local - self.zoom_offset
                pos_local = (
                    pos_local / self.zoom_factor
                    + QPoint(self.zoom_size.width(), self.zoom_size.height())
                    / self.zoom_factor
                )
                pos = self.mapToGlobal(pos_local)
                self.click_made.emit(pos)
                self.setVisible(False)
            else:
                self.setVisible(False)

    def enable(self, pos):
        self.setVisible(True)

        zoom_point = pos - self.zoom_offset
        self.move(zoom_point)

        screen = pyautogui.screenshot()
        screen = ImageQt(screen)
        screen = QPixmap.fromImage(screen)
        crop_point = pos - self.crop_offset
        screen = screen.copy(QRect(crop_point * 1.25, self.crop_size * 1.25))
        screen = screen.scaled(self.zoom_size, Qt.KeepAspectRatio)
        self.setPixmap(screen)
