from .app_mode import AppMode

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from eye_tracking_provider import EyeTrackingData


class ViewMode(AppMode):
    keyPressed = Signal(str)

    def __init__(self, parent=None, event_handlers=None):
        super().__init__(parent, event_handlers)

    def _update_data(self, eye_tracking_data: EyeTrackingData):
        pass
