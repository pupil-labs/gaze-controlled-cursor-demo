import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import *

from pupil_labs.real_time_screen_gaze import marker_generator


class Marker(QLabel):
    def __init__(self, marker_id, alignment, size=250, brightness=170):
        super().__init__()
        self.id = marker_id
        self.marker_size = size
        self.brightness = brightness

        self.setAlignment(alignment)
        self._pixmap = self._createMarker()
        self.setPixmap(self._pixmap)

        # self.setFixedSize(self.marker_size, self.marker_size)
        # self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.setWindowFlag(Qt.WindowTransparentForInput)

    def paintEvent(self, event):
        res = super().paintEvent(event)
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 255 - self.brightness))

        return res

    def resizeEvent(self, event: QResizeEvent) -> None:
        self.setPixmap(self._pixmap.scaled(self.size(), Qt.KeepAspectRatio))

        return super().resizeEvent(event)

    def get_marker_verts(self):
        """Returns the markers coordinates in global screen space."""

        # The marker has a white border which should be ignored when calculating the vertex positions.
        rect = self.rect() - QMargins(
            self.marker_size / 8,
            self.marker_size / 8,
            self.marker_size / 8,
            self.marker_size / 8,
        )
        verts = [
            rect.topLeft(),
            rect.topRight(),
            rect.bottomLeft(),
            rect.bottomRight(),
        ]
        verts = [self.mapToGlobal(vert) for vert in verts]
        verts = [(vert.x(), vert.y()) for vert in verts]
        return verts

    def _createMarker(self):
        marker = marker_generator.generate_marker(self.id, flip_x=True, flip_y=True)
        image = QImage(10, 10, QImage.Format_Mono)
        image.fill(1)
        for y in range(marker.shape[0]):
            for x in range(marker.shape[1]):
                color = marker[y][x] // 255
                image.setPixel(x + 1, y + 1, color)

        # Convert the QImage to a QPixmap
        return QPixmap.fromImage(image)


# class Marker(QWidget):
#     def __init__(self, marker_id, size=250, brightness=255):
#         super().__init__()
#         self.id = marker_id
#         self.marker_size = size
#         self.brightness = brightness
#         self._pixmap = self._createMarker()

#         # self.setFixedSize(self.marker_size, self.marker_size)
#         self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         # self.setWindowFlag(Qt.WindowTransparentForInput)

#     def paintEvent(self, event):
#         with QPainter(self) as painter:
#             painter.drawPixmap(self.rect(), self._pixmap)
#             painter.fillRect(self.rect(), QColor(0, 0, 0, 255 - self.brightness))

#     def get_marker_verts(self):
#         """Returns the markers coordinates in global screen space."""

#         # The marker has a white border which should be ignored when calculating the vertex positions.
#         rect = self.rect() - QMargins(
#             self.marker_size / 8,
#             self.marker_size / 8,
#             self.marker_size / 8,
#             self.marker_size / 8,
#         )
#         verts = [
#             rect.topLeft(),
#             rect.topRight(),
#             rect.bottomLeft(),
#             rect.bottomRight(),
#         ]
#         verts = [self.mapToGlobal(vert) for vert in verts]
#         verts = [(vert.x(), vert.y()) for vert in verts]
#         return verts

#     def _createMarker(self):
#         marker = marker_generator.generate_marker(self.id, flip_x=True, flip_y=True)
#         image = QImage(10, 10, QImage.Format_Mono)
#         image.fill(1)
#         for y in range(marker.shape[0]):
#             for x in range(marker.shape[1]):
#                 color = marker[y][x] // 255
#                 image.setPixel(x + 1, y + 1, color)

#         # Convert the QImage to a QPixmap
#         return QPixmap.fromImage(image)
