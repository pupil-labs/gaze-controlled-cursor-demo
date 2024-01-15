from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import mss

from image_conversion import qimage_from_frame

import numpy as np

class SelectionZoom(QWidget):
    click_made = Signal(QPoint)

    def __init__(self):
        super().__init__()

        self.setWindowFlag(Qt.ToolTip) # bordless fullscreen

        self.mss = mss.mss()

        self.zoom_center = QPoint(0, 0)
        self.zoom_level = 4.0
        self.screenshot = None

        self._current_zoom = 1.0

        self.zoom_in_animation = QSequentialAnimationGroup()
        anim = QPropertyAnimation(self, b"current_zoom")
        anim.setDuration(1000)
        anim.setStartValue(1.0)
        anim.setEndValue(4.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.zoom_in_animation.addAnimation(anim)
        self.zoom_in_animation.addPause(1000)

        self.zoom_out_animation = QSequentialAnimationGroup()
        anim = QPropertyAnimation(self, b"current_zoom")
        anim.setDuration(self.zoom_in_animation.duration()/2)
        anim.setStartValue(4.0)
        anim.setEndValue(1.0)
        anim.finished.connect(self.hide)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.zoom_out_animation.addAnimation(anim)
        self.zoom_out_animation.addPause(3000)

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
        painter.drawImage(target, self.screenshot)

        # Render the main window here for the tags and gaze overlay
        QApplication.instance().main_window.render_as_overlay(painter)

    def update_data(self, eye_tracking_data):
        self.update()

        if eye_tracking_data.dwell_process < 1.0:
            return

        pos = QPoint(*eye_tracking_data.gaze)

        if not self.isVisible():
            self.zoom_center = pos

            app = QApplication.instance()
            app.main_window.hide()
            QTimer.singleShot(500, self._take_snapshot)

        else:
            if self.zoom_in_animation.state() == QAbstractAnimation.Running:
                return
            if self.zoom_out_animation.state() == QAbstractAnimation.Running:
                return

            scaled_center = self.zoom_center * self._current_zoom
            offset = scaled_center - self.zoom_center
            pos = (pos + offset) / self._current_zoom

            self.zoom_out_animation.start()
            self.zoom_out_animation.finished.connect(lambda: self.click_made.emit(pos), Qt.SingleShotConnection)


    def _take_snapshot(self):
        app = QApplication.instance()
        screenshot = self.mss.grab(self.mss.monitors[1])
        self.screenshot = qimage_from_frame(np.array(screenshot), QImage.Format_RGB32)

        self.setGeometry(QApplication.instance().primaryScreen().geometry())
        self.show()
        self.zoom_in_animation.start()

        app.main_window.showMaximized()
        app.main_window.raise_()#  // for MacOS
        app.main_window.activateWindow()# // for Windows
