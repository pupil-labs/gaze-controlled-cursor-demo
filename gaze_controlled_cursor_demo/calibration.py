import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import Pipeline

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from calibration_ui import MainWindow

from widgets.debug_window import DebugWindow
from eye_tracking_provider import EyeTrackingProvider as EyeTrackingProvider
import time
import joblib


class CalibrationApp(QApplication):
    def __init__(self):
        super().__init__()
        screen_size = self.primaryScreen().size()

        self.main_window = MainWindow(screen_size)
        self.main_window.marker_overlay.surface_changed.connect(self.on_surface_changed)
        self.main_window.key_pressed.connect(self.on_key_pressed)

        self.debug_window = DebugWindow()

        screen_size = (screen_size.width(), screen_size.height())
        self.eye_tracking_provider = EyeTrackingProvider(
            markers=self.main_window.marker_overlay.markers,
            screen_size=screen_size,
            use_calibrated_gaze=False,
        )

        self.setApplicationDisplayName("Gaze Control - Calibration")

        self.pollTimer = QTimer()
        self.pollTimer.setInterval(1000 / 30)
        self.pollTimer.timeout.connect(self.poll)
        self.pollTimer.start()

        self.target_start = None
        self.target_duration = None
        self.targets = self._generate_targets()

        self.total_target_time = 2.0
        self.target_acquisition_time = 0.75
        self.calibration_idx = 0

        self.training_data = []
        self.training_labels = []

    def _generate_targets(self):
        width = self.main_window.width()
        height = self.main_window.height()

        hor_padd = width * 0.11
        ver_padd = height * 0.015
        hor_targets = np.linspace(hor_padd, width - hor_padd, 6)
        ver_targets = np.linspace(ver_padd, height * 0.15, 3)
        top_targets = np.meshgrid(hor_targets, ver_targets)
        top_targets = [
            QPoint(*t) for t in zip(top_targets[0].flatten(), top_targets[1].flatten())
        ]

        hor_padd = width * 0.11
        ver_padd = height * 0.015
        hor_targets = np.linspace(hor_padd, width - hor_padd, 6)
        ver_targets = np.linspace(height - height * 0.15, height - ver_padd, 3)
        bot_targets = np.meshgrid(hor_targets, ver_targets)
        bot_targets = [
            QPoint(*t) for t in zip(bot_targets[0].flatten(), bot_targets[1].flatten())
        ]

        hor_padd = width * 0.015
        hor_targets = np.linspace(hor_padd, width - hor_padd, 8)
        ver_padd = height * 0.2
        ver_targets = np.linspace(ver_padd, height - ver_padd, 6)
        center_targets = np.meshgrid(hor_targets, ver_targets)
        center_targets = [
            QPoint(*t)
            for t in zip(center_targets[0].flatten(), center_targets[1].flatten())
        ]

        targets = np.concatenate([top_targets, center_targets, bot_targets])
        return targets

    def on_surface_changed(self):
        self.eye_tracking_provider.update_surface()

    def on_key_pressed(self, event):
        if event.key() == Qt.Key_Return:
            self.target_start = time.time()
            self.target_duration = 0.0

    def poll(self):
        eye_tracking_data = self.eye_tracking_provider.receive()

        target_location, target_color = self._calc_target()

        self.main_window.update_data(eye_tracking_data, target_location, target_color)
        self.debug_window.update_data(eye_tracking_data)

        if (
            self.target_start is not None
            and self.target_duration > self.target_acquisition_time
        ):
            self.training_data.append(eye_tracking_data.gaze)
            self.training_labels.append(self.targets[self.calibration_idx])

    def _calc_target(self):
        if self.target_start is None:
            target_location = None
            target_color = None
        else:
            self.target_duration = time.time() - self.target_start
            if self.target_duration > self.total_target_time:
                self.calibration_idx += 1
                self.target_start = time.time()
                self.target_duration = 0.0

            if self.calibration_idx >= len(self.targets):
                target_location = None
                self.target_start = None
                self.target_duration = None

                np.save("training_data.npy", np.array(self.training_data))
                np.save("training_labels.npy", np.array(self.training_labels))

                self._calc_calibration()
            else:
                target_location = self.targets[self.calibration_idx]

            if self.target_duration > self.target_acquisition_time:
                target_color = QColor(Qt.green)
            else:
                target_color = QColor(Qt.red)

        return target_location, target_color

    def _calc_calibration(self):
        training_data = np.load("training_data.npy", allow_pickle=True)
        training_labels = np.load("training_labels.npy", allow_pickle=True)
        training_labels = np.array(
            [(lambda p: (p.x(), p.y()))(p) for p in training_labels]
        )

        predictor = Pipeline(
            [
                ("poly", PolynomialFeatures(degree=3, include_bias=True)),
                ("linear", LinearRegression()),
            ]
        )

        predictor.fit(training_data, training_labels)
        joblib.dump(predictor, "predictor.pkl")

    def exec(self):
        self.main_window.show()
        self.debug_window.show()
        super().exec()
        self.eye_tracking_provider.close()


def run():
    app = CalibrationApp()
    app.exec()


if __name__ == "__main__":
    run()
