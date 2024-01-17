from enum import Enum
import json

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import pyautogui

from main_ui import MainWindow
from widgets.settings_widget import SettingsWidget
from widgets.debug_window import DebugWindow
from widgets.action_settings_widget import ActionSettingsWidget

from gaze_event_type import GazeEventType, TriggerEvent

from eye_tracking_provider import EyeTrackingProvider as EyeTrackingProvider

from encoder import create_property_dict
from actions import (
    EdgeActionConfig,
    ScreenEdge,
    Direction,
    DoNothingAction,
    LogAction,
    ScrollAction,
    ToggleKeyboardAction,
    HideKeyboardAction,
    ShowKeyboardAction,
    ToggleSettingsWindowAction,
    ToggleDebugWindowAction,
    ShowModeMenuAction,
)

pyautogui.FAILSAFE = False


class AppMode(Enum):
    View = 0
    Click = 1
    Zoom = 2
    Keyboard = 3
    Calibrate = 4


class GazeControlApp(QApplication):
    def __init__(self):
        super().__init__()
        self._mode = AppMode.View
        self._use_zoom = True

        self.setApplicationDisplayName("Gaze Control")

        screen_size = self.primaryScreen().size()
        self.main_window = MainWindow()
        self.main_window.marker_overlay.surface_changed.connect(self.on_surface_changed)
        self.main_window.surface_changed.connect(self.on_surface_changed)
        self.main_window.keyboard.keyPressed.connect(self.on_key_pressed)
        self.main_window.selection_zoom.click_made.connect(self.on_mouse_click)
        self.main_window.mode_menu.mode_changed.connect(
            lambda mode: setattr(self, "mode", mode)
        )

        self.main_window.setScreen(self.primaryScreen())
        self.main_window.selection_zoom.setScreen(self.primaryScreen())

        self.eye_tracking_provider = EyeTrackingProvider(
            markers=self.main_window.marker_overlay.markers,
            screen_size=(screen_size.width(), screen_size.height()),
            use_calibrated_gaze=True,
        )

        self.action_configs = []
        self._load_settings()

        self.settings_window = SettingsWidget()
        self.settings_window.add_object_page(
            [
                self.main_window.marker_overlay,
                self.eye_tracking_provider.dwell_detector,
                self,
                self.main_window.selection_zoom,
            ],
            "Options",
        )
        self.action_settings_widget = ActionSettingsWidget(self.action_configs)
        self.action_settings_widget.action_config_added.connect(self.add_action_config)
        self.action_settings_widget.action_config_deleted.connect(
            self.delete_action_config
        )
        self.settings_window.add_page(self.action_settings_widget, "Edge Actions")
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
        self.main_window.selection_zoom.changed.connect(self.save_settings)
        self.eye_tracking_provider.dwell_detector.changed.connect(self.save_settings)

        self.mode = AppMode.View

    @property
    def mode(self) -> AppMode:
        return self._mode

    @mode.setter
    def mode(self, value):
        if type(value) == str:
            value = AppMode[value]

        self._mode = value
        self._clear_mode_artefacts()

        if value == AppMode.View:
            pass
        elif value == AppMode.Click:
            pass
        elif value == AppMode.Zoom:
            self.main_window.selection_zoom.setVisible(True)
        elif value == AppMode.Keyboard:
            self.main_window.keyboard.setVisible(True)
        elif value == AppMode.Calibrate:
            raise NotImplementedError()
        else:
            raise ValueError(f"Unknown mode {value}")

    def _clear_mode_artefacts(self):
        self.main_window.keyboard.setVisible(False)
        self.main_window.selection_zoom.setVisible(False)

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
            "selection_zoom": create_property_dict(self.main_window.selection_zoom),
            "edge_event_actions": [],
        }

        for action in self.action_configs:
            settings["edge_event_actions"].append(create_property_dict(action))

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
            setattr(self.main_window.selection_zoom, k, v)

        for action_config_meta in settings["edge_event_actions"]:
            action_config = EdgeActionConfig()
            for k, v in action_config_meta.items():
                if k == "action" and v is not None:
                    match v["__class__"]:
                        case "DoNothingAction":
                            action_config.action = DoNothingAction()
                        case "LogAction":
                            action_config.action = LogAction()
                        case "ScrollAction":
                            action_config.action = ScrollAction()
                            v["direction"] = Direction[v["direction"]]
                        case "HideKeyboardAction":
                            action_config.action = HideKeyboardAction()
                        case "ShowKeyboardAction":
                            action_config.action = ShowKeyboardAction()
                        case "ToggleKeyboardAction":
                            action_config.action = ToggleKeyboardAction()
                        case "ToggleSettingsWindowAction":
                            action_config.action = ToggleSettingsWindowAction()
                        case "ToggleDebugWindowAction":
                            action_config.action = ToggleDebugWindowAction()
                        case "ShowModeMenuAction":
                            action_config.action = ShowModeMenuAction()

                    if action_config.action is not None:
                        for action_k, action_v in v.items():
                            if action_k.startswith("__"):
                                continue

                            setattr(action_config.action, action_k, action_v)
                else:
                    if k == "screen_edge":
                        v = ScreenEdge[v]
                    elif k == "event":
                        v = GazeEventType[v]

                    setattr(action_config, k, v)

            self.add_action_config(action_config)

    def add_action_config(self, ac):
        ac.changed.connect(self.save_settings)
        self.action_configs.append(ac)

    def delete_action_config(self, ac):
        self.action_configs.remove(ac)

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

    def on_key_pressed(self, key):
        pyautogui.press(key)

    def hideEvent(self, event):
        print("no!")

    def poll(self):
        eye_tracking_data = self.eye_tracking_provider.receive()

        if eye_tracking_data is None:
            return

        mode_change = self._update_persistent_components(eye_tracking_data)
        if not mode_change:
            self._update_transient_components(eye_tracking_data)

    def _update_persistent_components(self, eye_tracking_data):
        self.main_window.update_data(eye_tracking_data)
        self.debug_window.update_data(eye_tracking_data)
        mode_change = self.main_window.mode_menu.update_data(eye_tracking_data)

        if eye_tracking_data.gaze is not None:
            for action_config in self.action_configs:
                if None in [
                    action_config.screen_edge,
                    action_config.event,
                    action_config.action,
                ]:
                    return

                trigger_event = TriggerEvent(action_config, eye_tracking_data)

                if action_config.polygon is None:
                    action_config.polygon = action_config.screen_edge.get_polygon(
                        self.main_window.screen()
                    )

                if action_config.polygon.containsPoint(
                    QPointF(*eye_tracking_data.gaze), Qt.OddEvenFill
                ):
                    if not action_config.has_gaze:
                        action_config.has_gaze = True
                        if action_config.event == GazeEventType.GAZE_ENTER:
                            action_config.action.execute(trigger_event)

                    if action_config.event == GazeEventType.GAZE_UPON:
                        action_config.action.execute(trigger_event)

                    if action_config.event == GazeEventType.FIXATE:
                        if eye_tracking_data.dwell_process == 1.0:
                            action_config.action.execute(trigger_event)

                else:
                    if action_config.has_gaze:
                        action_config.has_gaze = False
                        if action_config.event == GazeEventType.GAZE_EXIT:
                            action_config.action.execute(trigger_event)

        return mode_change

    def _update_transient_components(self, eye_tracking_data):
        if self.mode == AppMode.View:
            return
        elif self.mode == AppMode.Click:
            if eye_tracking_data.dwell_process == 1.0:
                self.on_mouse_click(QPoint(*eye_tracking_data.gaze))
        elif self.mode == AppMode.Zoom:
            self.main_window.selection_zoom.update_data(eye_tracking_data)
        elif self.mode == AppMode.Keyboard:
            if eye_tracking_data.dwell_process == 1.0:
                self.main_window.keyboard.update_data(eye_tracking_data.gaze)
        elif self.mode == AppMode.Calibrate:
            pass

    def exec(self):
        self.settings_window.show()

        super().exec()
        self.eye_tracking_provider.close()


def run():
    app = GazeControlApp()
    app.exec()


if __name__ == "__main__":
    run()
