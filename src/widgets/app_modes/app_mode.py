from typing import List, Callable

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from eye_tracking_provider import EyeTrackingData


class AppMode(QWidget):
    def __init__(
        self, parent: QWidget = None, event_handlers: dict[str, Callable] = None
    ):
        super().__init__(parent)
        self.event_handlers = event_handlers
        self.deactivate()

    def activate(self):
        self.active = True
        self.setVisible(True)

    def deactivate(self):
        self.active = True
        self.setVisible(False)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def update_data(self, eye_tracking_data: EyeTrackingData):
        if self.active:
            self._update_data(eye_tracking_data)

    def _update_data(self, eye_tracking_data: EyeTrackingData):
        raise NotImplementedError
