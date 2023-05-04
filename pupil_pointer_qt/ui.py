import pkg_resources

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

def locateAsset(*resourceParts):
    resource = '/'.join(['assets'] + list(resourceParts))
    return pkg_resources.resource_filename(__name__, resource)

class TagWindow(QWidget):
    surfaceChanged = Signal()
    mouseEnableChanged = Signal(bool)
    dwellRadiusChanged = Signal(int)
    dwellTimeChanged = Signal(float)

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setStyleSheet('* { font-size: 18pt }')

        self.pixmaps = []
        for tagID in range(4):
            tagImage = f'tag36_11_{tagID:05d}.png'
            self.pixmaps.append(QPixmap(locateAsset(tagImage)))

        self.point = (0, 0)
        self.clicked = False
        self.settingsVisible = True
        self.visibleMarkerIds = []

        self.form = QWidget()
        self.form.setLayout(QFormLayout())

        self.tagSizeInput = QSpinBox()
        self.tagSizeInput.setRange(10, 512)
        self.tagSizeInput.setValue(256)
        self.tagSizeInput.valueChanged.connect(self.onTagSizeChanged)

        self.tagBrightnessInput = QSpinBox()
        self.tagBrightnessInput.setRange(0, 255)
        self.tagBrightnessInput.setValue(128)
        self.tagBrightnessInput.valueChanged.connect(lambda _: self.repaint())

        self.dwellRadiusInput = QSpinBox()
        self.dwellRadiusInput.setRange(0, 512)
        self.dwellRadiusInput.setValue(25)
        self.dwellRadiusInput.valueChanged.connect(self.dwellRadiusChanged.emit)

        self.dwellTimeInput = QDoubleSpinBox()
        self.dwellTimeInput.setRange(0, 20)
        self.dwellTimeInput.setValue(0.75)
        self.dwellTimeInput.valueChanged.connect(self.dwellTimeChanged.emit)

        self.mouseEnabledInput = QCheckBox('Mouse Control')
        self.mouseEnabledInput.setChecked(False)
        self.mouseEnabledInput.toggled.connect(self.mouseEnableChanged.emit)

        self.form.layout().addRow('Tag Size', self.tagSizeInput)
        self.form.layout().addRow('Tag Brightness', self.tagBrightnessInput)
        self.form.layout().addRow('Dwell Radius', self.dwellRadiusInput)
        self.form.layout().addRow('Dwell Time', self.dwellTimeInput)
        self.form.layout().addRow('', self.mouseEnabledInput)

        self.instructionsLabel = QLabel('Right-click one of the tags to toggle settings view.')
        self.instructionsLabel.setAlignment(Qt.AlignHCenter)

        self.statusLabel = QLabel()
        self.statusLabel.setAlignment(Qt.AlignHCenter)

        self.setLayout(QGridLayout())
        self.layout().setSpacing(50)

        self.layout().addWidget(self.instructionsLabel, 0, 0, 1, 3)
        self.layout().addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding), 1, 1, 1, 1)
        self.layout().addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 2, 0, 1, 1)
        self.layout().addItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum), 2, 2, 1, 1)
        self.layout().addWidget(self.form, 3, 1, 1, 1)
        self.layout().addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding), 4, 1, 1, 1)
        self.layout().addWidget(self.statusLabel, 5, 0, 1, 3)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.RightButton:
            self.setSettingsVisible(not self.settingsVisible)

    def setSettingsVisible(self, visible):
        self.settingsVisible = visible
        self.updateMask()

    def setStatus(self, status):
        self.statusLabel.setText(status)

    def setClicked(self, clicked):
        self.clicked = clicked
        self.repaint()

    def updatePoint(self, norm_x, norm_y):
        tagMargin = 0.1 * self.tagSizeInput.value()
        surfaceSize = (
            self.width() - 2*tagMargin,
            self.height() - 2*tagMargin,
        )

        self.point = (
            norm_x*surfaceSize[0] + tagMargin,
            (surfaceSize[1] - norm_y*surfaceSize[1]) + tagMargin
        )

        self.repaint()
        return self.mapToGlobal(QPoint(*self.point))

    def showMarkerFeedback(self, markerIds):
        self.visibleMarkerIds = markerIds
        self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)

        if self.settingsVisible:
            if self.clicked:
                painter.setBrush(Qt.red)
            else:
                painter.setBrush(Qt.white)

            painter.drawEllipse(QPoint(*self.point), self.dwellRadiusInput.value(), self.dwellRadiusInput.value())

        for cornerIdx in range(4):
            cornerRect = self.getCornerRect(cornerIdx)
            if cornerIdx not in self.visibleMarkerIds:
                painter.fillRect(cornerRect.marginsAdded(QMargins(5, 5, 5, 5)), QColor(255, 0, 0))

            painter.drawPixmap(cornerRect, self.pixmaps[cornerIdx])
            painter.fillRect(cornerRect, QColor(0, 0, 0, 255-self.tagBrightnessInput.value()))

    def resizeEvent(self, event):
        self.updateMask()
        self.surfaceChanged.emit()

    def onTagSizeChanged(self, value):
        self.repaint()
        self.surfaceChanged.emit()

    def getMarkerSize(self):
        return self.tagSizeInput.value()

    def getSurfaceSize(self):
        tagMargin = self.getMarkerSize()/5
        return (self.width() - tagMargin, self.height() - tagMargin)

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
        tagSize = self.tagSizeInput.value()
        if cornerIdx == 0:
            return QRect(0, 0, tagSize, tagSize)

        elif cornerIdx == 1:
            return QRect(self.width()-tagSize, 0, tagSize, tagSize)

        elif cornerIdx == 2:
            return QRect(self.width()-tagSize, self.height()-tagSize, tagSize, tagSize)

        elif cornerIdx == 3:
            return QRect(0, self.height()-tagSize, tagSize, tagSize)
