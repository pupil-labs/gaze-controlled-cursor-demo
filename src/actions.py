import sys
from enum import Enum, auto
from PySide6.QtCore import QObject

if sys.platform == "win32":
    import win32api
    import win32con

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtMultimedia import QSoundEffect

import pyautogui

from gaze_event_type import GazeEventType, TriggerEvent
from eye_tracking_provider import EyeTrackingData

registered_actions = []


class Action(QObject):
    changed = Signal()

    def __init_subclass__(cls):
        registered_actions.append(cls)

    def execute(self, trigger_event):
        pass


class ScreenEdge(Enum):
    TOP_LEFT = auto()
    TOP_MIDDLE = auto()
    TOP_RIGHT = auto()
    LEFT_TOP = auto()
    LEFT_MIDDLE = auto()
    LEFT_BOTTOM = auto()
    RIGHT_TOP = auto()
    RIGHT_MIDDLE = auto()
    RIGHT_BOTTOM = auto()
    BOTTOM_LEFT = auto()
    BOTTOM_MIDDLE = auto()
    BOTTOM_RIGHT = auto()

    def get_polygon(self, screen):
        margin = 500
        w = screen.size().width()
        h = screen.size().height()
        match self:
            case ScreenEdge.TOP_LEFT:
                return QPolygonF(QRectF(0, -margin, w / 3, margin))
            case ScreenEdge.TOP_MIDDLE:
                return QPolygonF(QRectF(w / 3, -margin, w / 3, margin))
            case ScreenEdge.TOP_RIGHT:
                return QPolygonF(QRectF((w / 3) * 2, -margin, w / 3, margin))
            case ScreenEdge.LEFT_TOP:
                return QPolygonF(QRectF(-margin, 0, margin, h / 3))
            case ScreenEdge.LEFT_MIDDLE:
                return QPolygonF(QRectF(-margin, h / 3, margin, h / 3))
            case ScreenEdge.LEFT_BOTTOM:
                return QPolygonF(QRectF(-margin, (h / 3) * 2, margin, h / 3))
            case ScreenEdge.RIGHT_TOP:
                return QPolygonF(QRectF(w, 0, margin, h / 3))
            case ScreenEdge.RIGHT_MIDDLE:
                return QPolygonF(QRectF(w, h / 3, margin, h / 3))
            case ScreenEdge.RIGHT_BOTTOM:
                return QPolygonF(QRectF(w, (h / 3) * 2, margin, h / 3))
            case ScreenEdge.BOTTOM_LEFT:
                return QPolygonF(QRectF(0, h, w / 3, margin))
            case ScreenEdge.BOTTOM_MIDDLE:
                return QPolygonF(QRectF(w / 3, h, w / 3, margin))
            case ScreenEdge.BOTTOM_RIGHT:
                return QPolygonF(QRectF((w / 3) * 2, h, w / 3, margin))

    def __str__(self):
        return self.name.replace("_", " ").title()


class EdgeActionConfig(QObject):
    changed = Signal()

    def __init__(self):
        super().__init__()

        self._edge = None
        self._event = None
        self._action = None

        self.polygon = None
        self.has_gaze = False

    @property
    def screen_edge(self) -> ScreenEdge:
        return self._edge

    @screen_edge.setter
    def screen_edge(self, value):
        self._edge = value
        self.changed.emit()

    @property
    def event(self) -> GazeEventType:
        return self._event

    @event.setter
    def event(self, value):
        self._event = value
        self.changed.emit()

    @property
    def action(self) -> Action:
        return self._action

    @action.setter
    def action(self, value):
        self._action = value
        if self._action is not None:
            self._action.changed.connect(self.changed.emit)
        self.changed.emit()


class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()


class DoNothingAction(Action):
    friendly_name = "Do Nothing"


class LogAction(Action):
    friendly_name = "Log"

    def __init__(self):
        super().__init__()
        self._message = "FLAG"

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value):
        self._message = value
        self.changed.emit()

    def execute(self, trigger_event):
        print("Log action:", self._message)


class ScrollAction(Action):
    friendly_name = "Scroll"

    def __init__(self):
        super().__init__()
        self._direction = Direction.UP
        self._magnitude = 1

    @property
    def direction(self) -> Direction:
        return self._direction

    @direction.setter
    def direction(self, value):
        self._direction = value
        self.changed.emit()

    @property
    def magnitude(self) -> int:
        """
        :min 1
        :max 500
        """
        return self._magnitude

    @magnitude.setter
    def magnitude(self, value):
        self._magnitude = value
        self.changed.emit()

    def execute(self, trigger_event):
        magnitude = self._magnitude
        if self._direction in [Direction.LEFT, Direction.DOWN]:
            magnitude *= -1

        if self._direction in [Direction.LEFT, Direction.RIGHT]:
            pyautogui.hscroll(magnitude)
        else:
            if sys.platform == "win32":
                self._windows_scroll(magnitude)
            else:
                pyautogui.scroll(magnitude)

    def _windows_scroll(self, clicks):
        if clicks > 0:
            increment = win32con.WHEEL_DELTA
        else:
            increment = win32con.WHEEL_DELTA * -1

        for _ in range(int(abs(clicks))):
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, increment, 0)


class HideKeyboardAction(Action):
    friendly_name = "Hide Keyboard"

    def execute(self, trigger_event):
        QApplication.instance().main_window.keyboard.toggleKeyboard(False)


class ShowKeyboardAction(Action):
    friendly_name = "Show Keyboard"

    def execute(self, trigger_event):
        QApplication.instance().main_window.keyboard.toggleKeyboard(True)


class ToggleKeyboardAction(Action):
    friendly_name = "Toggle Keyboard"

    def execute(self, trigger_event):
        QApplication.instance().main_window.keyboard.toggleKeyboard()


class ToggleSettingsWindowAction(Action):
    friendly_name = "Toggle Settings Window"

    def execute(self, trigger_event):
        QApplication.instance().toggle_settings_window()


class ToggleDebugWindowAction(Action):
    friendly_name = "Toggle Debug Window"

    def execute(self, trigger_event):
        QApplication.instance().toggle_debug_window()


class ShowModeMenuAction(Action):
    friendly_name = "Show Mode Menu"

    def execute(self, trigger_event):
        QApplication.instance().main_window.mode_menu.setVisible(True)


class KeyPressAction(Action):
    friendly_name = "Press Key"
    key_pressed = Signal(str)

    def __init__(self, key_code) -> None:
        super().__init__()
        self.key_code = key_code
        self.key_sound = QSoundEffect()
        self.key_sound.setSource(QUrl.fromLocalFile("key-stroke.wav"))

    def execute(self, _):
        self.key_sound.play()
        self.key_pressed.emit(self.key_code)


class EdgeActionHandler:
    def __init__(self, screen, action_configs):
        self.screen = screen
        self.action_configs = action_configs

    def update_data(self, eye_tracking_data: EyeTrackingData):
        if eye_tracking_data is not None and eye_tracking_data.gaze is not None:
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
                        self.screen
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
