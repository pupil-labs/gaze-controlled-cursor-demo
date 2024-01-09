from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class GazeOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.gaze_circle_radius = 15.0
        self.gaze = None

    def update_data(self, gaze):
        self.gaze = gaze
        self.update()

    def paintEvent(self, event):
        with QPainter(self) as painter:
            if self.gaze is not None:
                red = QColor(Qt.red)
                red.setAlphaF(0.3)
                painter.setBrush(red)
                painter.drawEllipse(
                    self.gaze,
                    self.gaze_circle_radius,
                    self.gaze_circle_radius,
                )


class DebugWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.raw_gaze = None
        self.scene = None

        self.gaze_circle_radius = 20.0

        self.setWindowTitle("Debug Window - Scene Camera")
        self.setFixedSize(800, 600)

        layout = QVBoxLayout()
        self.img_label = QLabel()
        self.img_label.setText("")
        self.img_label.setScaledContents(True)
        self.img_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.img_label)
        self.setLayout(layout)

        self.gaze_overlay = GazeOverlay()
        self.gaze_overlay.setParent(self)
        self.gaze_overlay.setFixedSize(self.size())

    def update_data(self, data):
        if data is None:
            return

        self.scene = data.scene

        scene = self.scene.bgr_pixels
        height, width, _ = scene.shape
        bytesPerLine = 3 * width
        qImg = QImage(scene.data, width, height, bytesPerLine, QImage.Format_BGR888)
        pixmap = QPixmap(qImg)
        self.img_label.setPixmap(pixmap)

        if data.raw_gaze is not None:
            self.gaze_overlay.update_data(
                QPoint(data.raw_gaze.x, data.raw_gaze.y) * 0.5
            )

        # if data.raw_gaze is not None:
        #     self.raw_gaze = QPoint(data.raw_gaze.x, data.raw_gaze.y) * 0.5
        # else:
        #     self.raw_gaze = None

    #     self.update()

    # def paintEvent(self, event):
    #     if self.scene is not None:
    #         scene = self.scene.bgr_pixels
    #         height, width, _ = scene.shape
    #         bytesPerLine = 3 * width
    #         qImg = QImage(scene.data, width, height, bytesPerLine, QImage.Format_BGR888)
    #         pixmap = QPixmap(qImg)

    #         # if self.raw_gaze is not None:
    #         #     with QPainter(pixmap) as painter:
    #         #         if self.raw_gaze is not None:
    #         #             red = QColor(Qt.red)
    #         #             # red.setAlphaF(0.3)
    #         #             painter.setBrush(red)
    #         #             painter.drawEllipse(
    #         #                 self.raw_gaze,
    #         #                 self.gaze_circle_radius,
    #         #                 self.gaze_circle_radius,
    #         #             )

    #         self.img_label.setPixmap(pixmap)
