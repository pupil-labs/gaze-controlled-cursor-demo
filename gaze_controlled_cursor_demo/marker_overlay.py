from typing import Optional
from PySide6.QtCore import *
from PySide6.QtCore import Qt
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent, QPaintEvent, QResizeEvent
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QWidget

from eye_tracking_provider import Marker
import utils


class MarkerContainer(QWidget):
    def __init__(self, marker_id, alignment):
        super().__init__()
        self.alignment = alignment
        self.border_width = 5

        self.marker = Marker(marker_id, alignment)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.marker, alignment=alignment)
        self.setLayout(layout)
        # self.marker.setParent(self)

    def paintEvent(self, event: QPaintEvent) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        size = self.marker.pixmap().rect().size()
        pos = self.marker.mapToParent(self.marker.rect().topLeft())
        rect = QRect(pos, size)

        if self.alignment == Qt.AlignLeft | Qt.AlignTop:
            rect += QMargins(0, 0, self.border_width, self.border_width)
        elif self.alignment == Qt.AlignLeft | Qt.AlignBottom:
            rect += QMargins(0, self.border_width, self.border_width, 0)
        elif self.alignment == Qt.AlignRight | Qt.AlignTop:
            rect += QMargins(self.border_width, 0, 0, self.border_width)
        elif self.alignment == Qt.AlignRight | Qt.AlignBottom:
            rect += QMargins(self.border_width, self.border_width, 0, 0)

        painter.fillRect(rect, QColor(255, 0, 0, 255))

    def resizeEvent(self, event: QResizeEvent) -> None:
        edge = min(self.width(), self.height()) * 0.95
        self.marker.setFixedSize(edge, edge)

    def get_marker_verts(self):
        return self.marker.get_marker_verts()


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

        m = MarkerContainer(0, Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(m, 0, 0, 3, 2)
        markers.append(m)

        m = MarkerContainer(1, Qt.AlignLeft | Qt.AlignBottom)
        layout.addWidget(m, 13, 0, 3, 2)
        markers.append(m)

        m = MarkerContainer(2, Qt.AlignRight | Qt.AlignTop)
        layout.addWidget(m, 0, 18, 3, 2)
        markers.append(m)

        m = MarkerContainer(3, Qt.AlignRight | Qt.AlignBottom)
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
