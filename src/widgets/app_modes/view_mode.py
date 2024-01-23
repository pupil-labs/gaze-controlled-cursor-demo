from .app_mode import AppMode

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from eye_tracking_provider import EyeTrackingData
from widgets.gaze_overlay import GazeOverlay
from gaze_event_type import GazeEventType, TriggerEvent

import actions


class ViewMode(AppMode):
    keyPressed = Signal(str)

    def __init__(self, parent=None, event_handlers=None):
        super().__init__(parent, event_handlers)
        self.gaze_overlay = GazeOverlay(self)

        edge_action_configs = []

        a_config = actions.EdgeActionConfig()
        a = actions.ScrollAction()
        a.direction = actions.Direction.UP
        a_config.action = a
        a_config.event = GazeEventType.GAZE_UPON
        a_config.screen_edge = actions.ScreenEdge.TOP_MIDDLE
        edge_action_configs.append(a_config)

        a_config = actions.EdgeActionConfig()
        a = actions.ScrollAction()
        a.direction = actions.Direction.DOWN
        a_config.action = a
        a_config.event = GazeEventType.GAZE_UPON
        a_config.screen_edge = actions.ScreenEdge.BOTTOM_MIDDLE
        edge_action_configs.append(a_config)

        self.edge_action_handler = actions.EdgeActionHandler(
            QApplication.primaryScreen(), edge_action_configs
        )

    def _update_data(self, eye_tracking_data: EyeTrackingData):
        self.gaze_overlay.update_data(eye_tracking_data)
        self.edge_action_handler.update_data(eye_tracking_data)

    def resize(self, size):
        super().resize(size)
        self.gaze_overlay.setGeometry(0, 0, size.width(), size.height())
