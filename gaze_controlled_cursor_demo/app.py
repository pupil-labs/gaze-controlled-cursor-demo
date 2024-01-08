import sys
import json

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import pyautogui
import time
import pygame

pygame.init()


from ui import MainWindow

from debug_window import DebugWindow


from eye_tracking_provider import DummyEyeTrackingProvider as EyeTrackingProvider

pyautogui.FAILSAFE = False


class GazeControlApp(QApplication):
    def __init__(self):
        super().__init__()
        screen_size = self.primaryScreen().size()
        self.main_window = MainWindow(screen_size)
        self.main_window.marker_overlay.surface_changed.connect(self.on_surface_changed)

        self.debug_window = DebugWindow()

        self.key_sound = pygame.mixer.Sound("key-stroke.mp3")
        self.main_window.keyboard.keyPressed.connect(self.on_key_pressed)

        screen_size = (screen_size.width(), screen_size.height())
        self.eye_tracking_provider = EyeTrackingProvider(
            markers=self.main_window.marker_overlay.markers, screen_size=screen_size
        )

        self.setApplicationDisplayName("Gaze Control")

        self.pollTimer = QTimer()
        self.pollTimer.setInterval(1000 / 30)
        self.pollTimer.timeout.connect(self.poll)
        self.pollTimer.start()

    def on_surface_changed(self):
        self.eye_tracking_provider.update_surface()

    def on_key_pressed(self, key):
        pygame.mixer.Sound.play(self.key_sound)
        pyautogui.keyDown(key)

    def poll(self):
        eye_tracking_data = self.eye_tracking_provider.receive()

        if eye_tracking_data is None:
            return

        self.main_window.update_data(
            eye_tracking_data.gaze, eye_tracking_data.dwell_process
        )

        self.debug_window.update_data(eye_tracking_data)
        if eye_tracking_data.dwell_process == 1.0:
            self.main_window.keyboard.update_data(eye_tracking_data.gaze)

        if not self.main_window.keyboard.enabled:
            x, y = eye_tracking_data.gaze
            pyautogui.moveTo(x * 1.25, y * 1.25)

            if eye_tracking_data.dwell_process == 1.0:
                pyautogui.click()

    def exec(self):
        self.main_window.show()
        self.debug_window.show()
        super().exec()
        self.eye_tracking_provider.close()


def run():
    app = GazeControlApp()
    app.exec()
