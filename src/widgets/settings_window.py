from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")

        dialogLayout = QVBoxLayout()
        formLayout = QFormLayout()

        self.marker_brightness = QSlider()
        self.marker_brightness.setOrientation(Qt.Horizontal)
        self.marker_brightness.setMinimum(0)
        self.marker_brightness.setMaximum(255)
        self.marker_brightness.setValue(128)
        self.marker_brightness.setTickInterval(1)
        formLayout.addRow("Marker Brightness:", self.marker_brightness)

        dialogLayout.addLayout(formLayout)
        self.setLayout(dialogLayout)
