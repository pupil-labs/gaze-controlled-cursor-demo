from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import mss

from image_conversion import qimage_from_frame

import numpy as np

class SelectionZoom(QWidget):
    changed = Signal()
    click_made = Signal(QPoint)

    def __init__(self):
        super().__init__()

        self._current_zoom = 1.0
        self._zoom_offset_adjust = 1.2

        self.setWindowFlag(Qt.ToolTip) # bordless fullscreen

        self.mss = mss.mss()

        self.zoom_center = QPoint(0, 0)
        self.screenshot = None

        self.zoom_in_sequence = QSequentialAnimationGroup()
        self.zoom_in_animation = QPropertyAnimation(self, b"current_zoom")
        self.zoom_in_animation.setDuration(1000)
        self.zoom_in_animation.setStartValue(1.0)
        self.zoom_in_animation.setEndValue(4.0)
        self.zoom_in_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.zoom_in_sequence.addAnimation(self.zoom_in_animation)
        self.zoom_in_sequence.addPause(1000)

        self.zoom_out_sequence = QSequentialAnimationGroup()
        self.zoom_out_animation = QPropertyAnimation(self, b"current_zoom")
        self.zoom_out_animation.setDuration(self.zoom_in_sequence.duration()/2)
        self.zoom_out_animation.setStartValue(self.zoom_in_animation.endValue())
        self.zoom_out_animation.setEndValue(1.0)
        self.zoom_out_animation.finished.connect(self.hide)
        self.zoom_out_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.zoom_out_sequence.addAnimation(self.zoom_out_animation)
        self.zoom_out_sequence.addPause(3000)

    @property
    def scale_factor(self) -> float:
        """
        :min 0.0
        :max 100
        :decimals 2
        """
        return self.zoom_in_animation.endValue()

    @scale_factor.setter
    def scale_factor(self, value):
        self.zoom_in_animation.setEndValue(value)
        self.zoom_out_animation.setStartValue(value)

        self.changed.emit()

    @property
    def zoom_offset_multiplier(self) -> float:
        """
        :min 1.0
        :max 2.0
        :decimals 2
        :step 0.1
        """
        # @TODO: calculate this value dynamically based on scale_factor
        return self._zoom_offset_adjust

    @zoom_offset_multiplier.setter
    def zoom_offset_multiplier(self, value):
        self._zoom_offset_adjust = value
        self.changed.emit()

    @Property(float) # qt prop
    def current_zoom(self):
        return self._current_zoom

    @current_zoom.setter
    def current_zoom(self, value):
        self._current_zoom = value
        self.update()

    def paintEvent(self, event):
        scaled_center = self.zoom_center * self._current_zoom
        offset = scaled_center - self.zoom_center
        target = QRect(-offset, self.size()*self._current_zoom)

        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)
        painter.drawImage(target, self.screenshot)

        # Render the main window here for the tags and gaze overlay
        QApplication.instance().main_window.render_as_overlay(painter)

    def update_data(self, eye_tracking_data):
        self.update()

        if eye_tracking_data.dwell_process < 1.0:
            return

        pos = QPoint(*eye_tracking_data.gaze)

        if not self.isVisible():
            # set the zoom center just beyond the zoom point (as measured from the center)
            # this makes objects on the edge easier to hit
            screen_center = QPoint(self.screen().size().width()/2, self.screen().size().height()/2)
            pos -= screen_center
            pos *= self._zoom_offset_adjust
            pos += screen_center

            self.zoom_center = pos

            app = QApplication.instance()
            app.main_window.hide()
            QTimer.singleShot(500, self._take_snapshot)

        else:
            if self.zoom_in_sequence.state() == QAbstractAnimation.Running:
                return
            if self.zoom_out_sequence.state() == QAbstractAnimation.Running:
                return

            scaled_center = self.zoom_center * self._current_zoom
            offset = scaled_center - self.zoom_center
            pos = (pos + offset) / self._current_zoom

            self.zoom_out_sequence.start()
            self.zoom_out_animation.finished.connect(lambda: self.click_made.emit(pos), Qt.SingleShotConnection)


    def _take_snapshot(self):
        app = QApplication.instance()
        screenshot = self.mss.grab(self.mss.monitors[1])
        self.screenshot = qimage_from_frame(np.array(screenshot), QImage.Format_RGB32)

        self.setGeometry(QApplication.instance().primaryScreen().geometry())
        self.show()
        self.zoom_in_sequence.start()

        app.main_window.showMaximized()
        app.main_window.raise_()#  // for MacOS
        app.main_window.activateWindow()# // for Windows
