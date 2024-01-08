from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent, QResizeEvent
from PySide6.QtWidgets import *

from eye_tracking_provider import Marker
import utils


class MarkerOverlay(QWidget):
    surface_changed = Signal()

    def __init__(self):
        super().__init__()

        layout = QGridLayout()
        for i in range(20):
            layout.setColumnStretch(i, 1)
        for i in range(16):
            layout.setRowStretch(i, 1)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.markers = self._add_markers(layout)
        self.setLayout(layout)

    def _add_markers(self, layout):
        markers = []

        # Full grid of markers for debugging
        # for i in range(20):
        #     for j in range(16):
        #         m = Marker(i * 20 + j, Qt.AlignLeft | Qt.AlignTop)
        #         layout.addWidget(m, j, i, 1, 1)
        #         self.markers.append(m)

        m = Marker(0, Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(m, 0, 0, 3, 2)
        markers.append(m)

        m = Marker(1, Qt.AlignLeft | Qt.AlignBottom)
        layout.addWidget(m, 13, 0, 3, 2)
        markers.append(m)

        m = Marker(2, Qt.AlignRight | Qt.AlignTop)
        layout.addWidget(m, 0, 18, 3, 2)
        markers.append(m)

        m = Marker(3, Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(m, 13, 18, 3, 2)
        markers.append(m)

        return markers

    def update(self, gaze, dwell_process):
        if gaze is None:
            self.gaze_location = None
            self.dwell_process = None
        else:
            gaze = self.mapFromGlobal(QPoint(*gaze))
            dwell_process = dwell_process

            self.gaze_overlay.update(gaze, dwell_process)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.surface_changed.emit()
