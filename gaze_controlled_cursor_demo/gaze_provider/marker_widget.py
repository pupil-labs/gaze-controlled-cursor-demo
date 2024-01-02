import sys

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from pupil_labs.real_time_screen_gaze import marker_generator


def createMarker(marker_id):
    marker = marker_generator.generate_marker(marker_id, flip_x=True, flip_y=True)
    image = QImage(10, 10, QImage.Format_Mono)
    image.fill(1)
    for y in range(marker.shape[0]):
        for x in range(marker.shape[1]):
            color = marker[y][x] // 255
            image.setPixel(x + 1, y + 1, color)

    # Convert the QImage to a QPixmap
    return QPixmap.fromImage(image)


def pointToTuple(qpoint):
    return (qpoint.x(), qpoint.y())


class MarkerWidget(QWidget):
    surfaceChanged = Signal()
    mouseEnableChanged = Signal(bool)
    dwellRadiusChanged = Signal(int)
    dwellTimeChanged = Signal(float)
    smoothingChanged = Signal(float)

    def __init__(self):
        super().__init__()

        self.marker_size = 200
        self.marker_padding = self.marker_size / 8
        self.marker_brightness = 255

        # self.showFullScreen()
        # self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setWindowFlag(Qt.WindowStaysOnTopHint)

        self.markerIDs = [i for i in range(4)]
        self.pixmaps = [createMarker(i) for i in self.markerIDs]

        self.visibleMarkerIds = []

    def showMarkerFeedback(self, markerIds):
        self.visibleMarkerIds = markerIds
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)

        for cornerIdx in range(4):
            cornerRect = self.getCornerRect(cornerIdx)
            if cornerIdx not in self.visibleMarkerIds:
                painter.fillRect(
                    cornerRect.marginsAdded(QMargins(5, 5, 5, 5)), QColor(255, 0, 0)
                )

            painter.drawPixmap(cornerRect, self.pixmaps[cornerIdx])
            painter.fillRect(cornerRect, QColor(0, 0, 0, 255 - self.marker_brightness))

    def resizeEvent(self, event):
        # self.updateMask()
        # self.surfaceChanged.emit()
        pass

    def getMarkerVerts(self):
        markers_verts = {}

        for cornerIdx, markerID in enumerate(self.markerIDs):
            rect = self.getCornerRect(cornerIdx) - QMargins(
                self.marker_padding,
                self.marker_padding,
                self.marker_padding,
                self.marker_padding,
            )

            markers_verts[markerID] = [
                pointToTuple(rect.topLeft()),
                pointToTuple(rect.topRight()),
                pointToTuple(rect.bottomRight()),
                pointToTuple(rect.bottomLeft()),
            ]

        return markers_verts

    # TODO: Is this really correct? Don't we have the subtract the marker padding?
    def getSurfaceSize(self):
        return (self.width(), self.height())

    def updateMask(self):
        if self.settingsVisible:
            mask = QRegion(0, 0, self.width(), self.height())

        else:
            mask = QRegion(0, 0, 0, 0)
            for cornerIdx in range(4):
                rect = self.getCornerRect(cornerIdx).marginsAdded(QMargins(2, 2, 2, 2))
                mask = mask.united(rect)

        self.setMask(mask)

    def getCornerRect(self, cornerIdx):
        tagSize = self.marker_size
        tagSizePadded = tagSize + self.marker_padding * 2

        if cornerIdx == 0:
            return QRect(0, 0, tagSizePadded, tagSizePadded)

        elif cornerIdx == 1:
            return QRect(self.width() - tagSizePadded, 0, tagSizePadded, tagSizePadded)

        elif cornerIdx == 2:
            return QRect(
                self.width() - tagSizePadded,
                self.height() - tagSizePadded,
                tagSizePadded,
                tagSizePadded,
            )

        elif cornerIdx == 3:
            return QRect(0, self.height() - tagSizePadded, tagSizePadded, tagSizePadded)

    def surface_to_global_transform(self, norm_x, norm_y):
        surfaceSize = (
            self.width() - 2 * self.marker_padding,
            self.height() - 2 * self.marker_padding,
        )
        point = (
            norm_x * surfaceSize[0] + self.marker_padding,
            (surfaceSize[1] - norm_y * surfaceSize[1]) + self.marker_padding,
        )

        return self.mapToGlobal(QPoint(*point))
