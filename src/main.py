from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import pyautogui

from main_ui import MainWindow
from widgets.settings_window import SettingsWindow
from widgets.debug_window import DebugWindow


from eye_tracking_provider import DummyEyeTrackingProvider as EyeTrackingProvider

pyautogui.FAILSAFE = False


class GazeControlApp(QApplication):
    def __init__(self):
        super().__init__()
        screen_size = self.primaryScreen().size()
        self.main_window = MainWindow(screen_size)
        self.main_window.marker_overlay.surface_changed.connect(self.on_surface_changed)

        self.settings_window = SettingsWindow()
        self.settings_window.marker_brightness.valueChanged.connect(
            lambda value: self.main_window.marker_overlay.set_brightness(value)
        )
        self.debug_window = DebugWindow()

        self.main_window.keyboard.keyPressed.connect(self.on_key_pressed)

        screen_size = (screen_size.width(), screen_size.height())
        self.eye_tracking_provider = EyeTrackingProvider(
            markers=self.main_window.marker_overlay.markers,
            screen_size=screen_size,
            use_calibrated_gaze=True,
        )

        self.setApplicationDisplayName("Gaze Control")

        self.pollTimer = QTimer()
        self.pollTimer.setInterval(1000 / 30)
        self.pollTimer.timeout.connect(self.poll)
        self.pollTimer.start()

    def on_surface_changed(self):
        self.eye_tracking_provider.update_surface()

    def on_key_pressed(self, key):
        pyautogui.press(key)

    def poll(self):
        eye_tracking_data = self.eye_tracking_provider.receive()

        if eye_tracking_data is None:
            return

        self.main_window.update_data(eye_tracking_data)

        self.debug_window.update_data(eye_tracking_data)
        if eye_tracking_data.dwell_process == 1.0:
            self.main_window.keyboard.update_data(eye_tracking_data.gaze)

        if not self.main_window.keyboard.enabled:
            if eye_tracking_data.gaze is not None:
                x, y = eye_tracking_data.gaze
                pyautogui.moveTo(x * 1.25, y * 1.25)

            if eye_tracking_data.dwell_process == 1.0:
                pyautogui.click()

    def set_window_position(self):
        self.main_window.move(self.primaryScreen().geometry().topLeft())

    def exec(self):
        self.main_window.show()
        QTimer.singleShot(500, self.set_window_position)

        self.settings_window.show()
        self.debug_window.show()
        super().exec()
        self.eye_tracking_provider.close()


def run():
    app = GazeControlApp()
    app.exec()


if __name__ == "__main__":
    run()
