from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .ui.settings import Ui_Settings


class SettingsWindow(QWidget, Ui_Settings):
    device_changed = Signal(bool, str, int)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.device_auto_discovery.stateChanged.connect(self.on_device_auto_discovery)

    def on_device_auto_discovery(self, value):
        self.device_ip.setEnabled(not value)
        self.port.setEnabled(not value)
