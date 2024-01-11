from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .scaled_image_view import ScaledImageView

class GazeView(ScaledImageView):
    def __init__(self):
        super().__init__()
        self.gaze_circle_radius = 15.0
        self.gaze_point = None
        self.overlay_color = QColor(255, 0, 0, 77)

    def set_gaze(self, gaze):
        self.gaze_point = gaze
        self.update()

    def paintEvent(self, event):
        if self.image is None:
            return

        super().paintEvent(event)
        
        if self.gaze_point is not None:
            scale = self.render_rect.width() / self.image.width()
            offset = self.render_rect.topLeft()
            gaze_render_point = self.gaze_point * scale + offset

            painter = QPainter(self)
            painter.setBrush(self.overlay_color)
            painter.drawEllipse(
                gaze_render_point,
                self.gaze_circle_radius,
                self.gaze_circle_radius,
            )


class DebugWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setLayout(QVBoxLayout())

        self.raw_gaze = None
        self.scene = None

        self.setWindowTitle("Debug Window - Scene Camera")
        self.resize(800, 600)

        self.gaze_view = GazeView()
        self.layout().addWidget(self.gaze_view, stretch=1)

        self.info_widget = QLabel()
        self.info_widget.setStyleSheet("font-family: monospace")
        self.info_widget.setText("Waiting for stream...")
        self.layout().addWidget(self.info_widget)

    def update_data(self, data):
        if data is None:
            return

        self.scene = data.scene

        image = qimage_from_frame(self.scene.bgr_pixels)
        self.gaze_view.set_image(image)

        if data.raw_gaze is not None:
            device_info = QApplication.instance().eye_tracking_provider.device
            gaze_point = QPoint(data.raw_gaze.x, data.raw_gaze.y)
            self.info_widget.setText(f"Connected to {device_info}. Gaze: {gaze_point.x(): 4d}, {gaze_point.y(): 4d}")
            self.gaze_view.set_gaze(gaze_point)


def qimage_from_frame(frame):
	if frame is None:
		return QImage()

	if len(frame.shape) == 2:
		height, width = frame.shape
		channel = 1
		image_format = QImage.Format_Grayscale8
	else:
		height, width, channel = frame.shape
		image_format = QImage.Format_BGR888

	bytes_per_line = channel * width

	return QImage(frame.data, width, height, bytes_per_line, image_format)