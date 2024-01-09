from PySide6.QtCore import *
from PySide6.QtCore import Qt
from PySide6.QtGui import *
from PySide6.QtGui import QPaintEvent, QResizeEvent
from PySide6.QtWidgets import *
from PySide6.QtWidgets import QWidget

from eye_tracking_provider import Marker


class MarkerContainer(QWidget):
    marker_changed = Signal()

    def __init__(self, marker_id, alignment):
        super().__init__()
        self.marker_id = marker_id
        self.alignment = alignment
        self.border_width = 5
        self.detected = False

        self.marker = Marker(marker_id, alignment)
        self.marker.setParent(self)
        self._transform_marker()

    def _transform_marker(self):
        edge = min(self.width(), self.height()) * 0.95
        self.marker.setFixedSize(edge, edge)

        if self.alignment == Qt.AlignLeft | Qt.AlignTop:
            self.marker.move(0, 0)
        elif self.alignment == Qt.AlignLeft | Qt.AlignBottom:
            self.marker.move(0, self.height() - self.marker.height())
        elif self.alignment == Qt.AlignRight | Qt.AlignTop:
            self.marker.move(self.width() - self.marker.width(), 0)
        elif self.alignment == Qt.AlignRight | Qt.AlignBottom:
            self.marker.move(
                self.width() - self.marker.width(), self.height() - self.marker.height()
            )

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

        color = QColor(0, 255, 0, 255) if self.detected else QColor(255, 0, 0, 255)
        painter.fillRect(rect, color)

    def resizeEvent(self, event: QResizeEvent) -> None:
        self._transform_marker()
        self.marker_changed.emit()

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

        for m in markers:
            m.marker_changed.connect(self.on_marker_changed)

        return markers

    def on_marker_changed(self):
        self.surface_changed.emit()

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.surface_changed.emit()

    def update_data(self, detected_markers):
        for m in self.markers:
            m.detected = m.marker_id in detected_markers

        self.update()
