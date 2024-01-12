from PySide6.QtCore import *
from PySide6.QtCore import Qt
from PySide6.QtGui import *
from PySide6.QtGui import QPaintEvent, QResizeEvent
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QWidget

from eye_tracking_provider import Marker

class MarkerOverlay(QWidget):
    changed = Signal()
    surface_changed = Signal()
    brightness_changed = Signal(int)

    def __init__(self):
        super().__init__()

        self.setLayout(QGridLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setColumnStretch(1, 1)
        self.layout().setRowStretch(1, 1)

        self.markers = []

        m = Marker(0)
        self.layout().addWidget(m, 0, 0)
        self.markers.append(m)

        m = Marker(1)
        self.layout().addWidget(m, 0, 2)
        self.markers.append(m)

        m = Marker(2)
        self.layout().addWidget(m, 2, 0)
        self.markers.append(m)

        m = Marker(3)
        self.layout().addWidget(m, 2, 2)
        self.markers.append(m)

    @property
    def marker_brightness(self) -> int:
        """
        :min 0
        :max 255
        """
        return self.markers[0].brightness

    @marker_brightness.setter
    def marker_brightness(self, value):
        for m in self.markers:
            m.brightness = value

        self.changed.emit()

    @property
    def marker_size(self) -> int:
        """
        :min 100
        :max 1024
        """
        return self.markers[0].minimumWidth()

    @marker_size.setter
    def marker_size(self, value):
        for m in self.markers:
            m.setMinimumSize(value, value)

        self.changed.emit()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.surface_changed.emit()
