from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import pyautogui

from main_ui import MainWindow
from widgets.settings_window import SettingsWindow
from widgets.debug_window import DebugWindow


from eye_tracking_provider import EyeTrackingProvider as EyeTrackingProvider

pyautogui.FAILSAFE = False


class GazeControlApp(QApplication):
    def __init__(self):
        super().__init__()
        self.setApplicationDisplayName("Gaze Control")

        screen_size = self.primaryScreen().size()
        self.main_window = MainWindow()
        self.main_window.marker_overlay.surface_changed.connect(self.on_surface_changed)
        self.main_window.surface_changed.connect(self.on_surface_changed)
        self.main_window.keyboard.keyPressed.connect(self.on_key_pressed)

        self.eye_tracking_provider = EyeTrackingProvider(
            markers=self.main_window.marker_overlay.markers,
            screen_size=(screen_size.width(), screen_size.height()),
            use_calibrated_gaze=True,
        )
        self.settings_window = SettingsWindow(controller=self)
        self.debug_window = DebugWindow()
        self._build_tray_icon()

        self._load_settings()

        self.pollTimer = QTimer()
        self.pollTimer.setInterval(1000 / 30)
        self.pollTimer.timeout.connect(self.poll)
        self.pollTimer.start()

    def _build_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(QIcon("PPL-Favicon-144x144.png"))

        self.tray_menu = QMenu()
        self.actions = []
        self.tray_menu.addAction("Toggle Main Window").triggered.connect(lambda _: self.toggle_main_window())
        self.tray_menu.addAction("Toggle Debug Window").triggered.connect(lambda _: self.toggle_debug_window())
        self.tray_menu.addAction("Toggle Settings Window").triggered.connect(lambda _: self.toggle_settings_window())
        self.tray_menu.addSeparator()
        self.tray_menu.addAction("Quit").triggered.connect(lambda _: self.quit())
        
        self.tray_icon.setContextMenu(self.tray_menu)

        self.tray_icon.show()

    def toggle_main_window(self):
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.main_window.showMaximized()

    def toggle_debug_window(self):
        if self.debug_window.isVisible():
            self.debug_window.hide()
        else:
            self.debug_window.show()

    def toggle_settings_window(self):
        if self.settings_window.isVisible():
            self.settings_window.hide()
        else:
            self.settings_window.show()

    def _load_settings(self):
        self.main_window.marker_overlay.set_brightness(128)
        self.eye_tracking_provider.dwell_detector.dwell_time = 0.75

    def connect_to_device(self):
        result = self.eye_tracking_provider.connect(
            self.settings_window.device_auto_discovery.isChecked(),
            self.settings_window.device_ip.text(),
            int(self.settings_window.port.text()),
        )

        if result is None:
            self.settings_window.device_status.setText("Failed to connect")
        else:
            ip, port = result
            self.settings_window.on_connection_attempt(ip, port, "Connected")

            if not self.main_window.isVisible():
                self.main_window.showMaximized()
            if not self.debug_window.isVisible():
                self.debug_window.show()

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

    def exec(self):
        self.settings_window.show()
        super().exec()
        self.eye_tracking_provider.close()


def run():
    app = GazeControlApp()
    app.exec()


if __name__ == "__main__":
    run()
