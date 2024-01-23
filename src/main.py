import json

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import pyautogui

from main_ui import MainWindow
from widgets.settings_widget import SettingsWidget
from widgets.debug_window import DebugWindow


from eye_tracking_provider import EyeTrackingProvider as EyeTrackingProvider

from encoder import create_property_dict
import actions
from gaze_event_type import GazeEventType

# from hotkey_manager import HotkeyManager

pyautogui.FAILSAFE = False


class GazeControlApp(QApplication):
    def __init__(self):
        super().__init__()

        event_handlers = {
            "on_key_pressed": self.on_key_pressed,
            "on_mouse_click": self.on_mouse_click,
            "on_mouse_move": self.on_mouse_move,
            "on_surface_changed": self.on_surface_changed,
        }

        # self.hotkey_manager = HotkeyManager()
        # self.killswitch_key = QKeyCombination(
        #     Qt.ShiftModifier | Qt.ControlModifier, Qt.Key_K
        # )
        # self.pause_switch_key = QKeyCombination(
        #     Qt.ShiftModifier | Qt.ControlModifier, Qt.Key_P
        # )
        # self.hotkey_manager.hotkey_triggered.connect(self._on_hotkey_pressed)

        self.setApplicationDisplayName("Gaze Control")

        screen_size = self.primaryScreen().size()
        self.main_window = MainWindow(event_handlers)
        self.main_window.marker_overlay.surface_changed.connect(self.on_surface_changed)
        self.main_window.surface_changed.connect(self.on_surface_changed)
        self.main_window.setScreen(self.primaryScreen())

        self.eye_tracking_provider = EyeTrackingProvider(
            markers=self.main_window.marker_overlay.markers,
            screen_size=(screen_size.width(), screen_size.height()),
            use_calibrated_gaze=True,
        )

        edge_action_configs = []
        a_config = actions.EdgeActionConfig()
        a = actions.ShowModeMenuAction()
        a_config.action = a
        a_config.event = GazeEventType.GAZE_ENTER
        a_config.screen_edge = actions.ScreenEdge.LEFT
        edge_action_configs.append(a_config)
        self.edge_action_handler = actions.EdgeActionHandler(
            self.primaryScreen(), edge_action_configs
        )

        self._load_settings()

        self.settings_window = SettingsWidget()
        self.settings_window.add_object_page(
            [
                self,
                self.eye_tracking_provider.dwell_detector,
            ],
            "General Options",
        )
        self.settings_window.add_object_page(self.main_window.marker_overlay, "Markers")
        self.settings_window.add_object_page(
            self.main_window.modes["Zoom"].selection_zoom, "Zoom-clicking"
        )

        self.debug_window = DebugWindow()
        self._build_tray_icon()

        self.poll_timer = QTimer()
        self.poll_timer.setInterval(1000 / 30)
        self.poll_timer.timeout.connect(self.poll)
        self.poll_timer.start()

        # Delay saves to prevent hammering the disk
        self.save_timer = QTimer()
        self.save_timer.setSingleShot(True)
        self.save_timer.setInterval(500)
        self.save_timer.timeout.connect(self._save_settings)

        self.main_window.marker_overlay.changed.connect(self.save_settings)
        self.main_window.modes["Zoom"].selection_zoom.changed.connect(
            self.save_settings
        )
        self.eye_tracking_provider.dwell_detector.changed.connect(self.save_settings)

        self.pause_switch_active = False

    # @property
    # def killswitch_key(self) -> QKeyCombination:
    #     """
    #     :requires_modifier
    #     """
    #     return self.hotkey_manager.get_hotkey("killswitch")

    # @killswitch_key.setter
    # def killswitch_key(self, value):
    #     if isinstance(value, str):
    #         if value == "":
    #             value = None
    #         else:
    #             value = QKeySequence.fromString(value)[0]

    #     self.hotkey_manager.set_hotkey("killswitch", value)

    #     self.save_settings()

    # @property
    # def pause_switch_key(self) -> QKeyCombination:
    #     """
    #     :requires_modifier
    #     """
    #     return self.hotkey_manager.get_hotkey("pause_switch")

    # @pause_switch_key.setter
    # def pause_switch_key(self, value):
    #     if isinstance(value, str):
    #         if value == "":
    #             value = None
    #         else:
    #             value = QKeySequence.fromString(value)[0]

    #     self.hotkey_manager.set_hotkey("pause_switch", value)

    #     self.save_settings()

    # def _on_hotkey_pressed(self, action, key_combo):
    #     if action == "killswitch":
    #         self.quit()
    #     elif action == "pause_switch":
    #         self.pause_switch_active = not self.pause_switch_active

    def save_settings(self):
        try:
            self.save_timer.start()
        except AttributeError:
            pass

    def _save_settings(self):
        settings = {
            "main": create_property_dict(self),
            "marker_overlay": create_property_dict(self.main_window.marker_overlay),
            "dwell_detector": create_property_dict(
                self.eye_tracking_provider.dwell_detector
            ),
            "selection_zoom": create_property_dict(
                self.main_window.modes["Zoom"].selection_zoom
            ),
            "edge_event_actions": [],
        }

        with open("settings.json", "w") as output_file:
            json.dump(settings, output_file, indent=4)

    def _load_settings(self):
        try:
            with open("settings.json", "r") as input_file:
                settings = json.load(input_file)
        except Exception as exc:
            print("Failed to load settings", exc)
            return

        for k, v in settings["main"].items():
            setattr(self, k, v)

        for k, v in settings["marker_overlay"].items():
            setattr(self.main_window.marker_overlay, k, v)

        for k, v in settings["dwell_detector"].items():
            setattr(self.eye_tracking_provider.dwell_detector, k, v)

        for k, v in settings["selection_zoom"].items():
            setattr(self.main_window.modes["Zoom"].selection_zoom, k, v)

    def _build_tray_icon(self):
        icon_image = QImage("PPL-Favicon-144x144.png")

        desktop_dark_mode = (
            self.palette().window().color().value()
            < self.palette().windowText().color().value()
        )
        if desktop_dark_mode:
            icon_image.invertPixels()

        self.tray_icon = QSystemTrayIcon(QPixmap.fromImage(icon_image))

        self.tray_menu = QMenu()
        self.actions = []
        self.tray_menu.addAction("Toggle Main Window").triggered.connect(
            lambda _: self.toggle_main_window()
        )
        self.tray_menu.addAction("Toggle Debug Window").triggered.connect(
            lambda _: self.toggle_debug_window()
        )
        self.tray_menu.addAction("Toggle Settings Window").triggered.connect(
            lambda _: self.toggle_settings_window()
        )
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

    def connect_to_device(self, host, port):
        result = self.eye_tracking_provider.connect(ip=host, port=port)

        if result is None:
            # TODO: updating cevice status is broken
            # self.settings_window.device_status.setText("Failed to connect")
            print("Failed to connect")
            self.tray_icon.showMessage(
                "Gaze Control Connection", "Connection failed!", QSystemTrayIcon.Warning
            )

            return False

        else:
            ip, port = result
            self.tray_icon.showMessage(
                "Gaze Control Connection",
                f"Connected to {ip}:{port}!",
                QSystemTrayIcon.Information,
                3000,
            )

            if not self.main_window.isVisible():
                self.main_window.showMaximized()
            if not self.debug_window.isVisible():
                self.debug_window.show()

            return True

    def on_surface_changed(self):
        self.eye_tracking_provider.update_surface()

    def on_mouse_click(self, pos: QPoint):
        pyautogui.click(pos.x(), pos.y())

    def on_mouse_move(self, pos: QPoint):
        pyautogui.moveTo(pos.x(), pos.y())

    def on_key_pressed(self, key):
        pyautogui.press(key)

    def poll(self):
        eye_tracking_data = self.eye_tracking_provider.receive()
        self.debug_window.update_data(eye_tracking_data)

        self.edge_action_handler.update_data(eye_tracking_data)
        self.main_window.mode_menu.update_data(eye_tracking_data)
        mode_change = self.main_window.mode_menu.mode_change
        if not mode_change and not self.pause_switch_active:
            self.main_window.update_data(eye_tracking_data)

    def exec(self):
        self.settings_window.show()

        super().exec()
        self.eye_tracking_provider.close()


def run():
    app = GazeControlApp()
    app.exec()


if __name__ == "__main__":
    run()
