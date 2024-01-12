import sys
from enum import Enum, auto

if sys.platform == "win32":
    import win32api
    import win32con

from PySide6.QtGui import QPolygonF
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QRectF, Signal, QObject

import pyautogui

from gaze_event_type import GazeEventType

registered_actions = []


class Action(QObject):
    changed = Signal()

    def __init_subclass__(cls):
        registered_actions.append(cls)

    def execute(self, trigger_event):
        pass

class ScreenEdge(Enum):
    TOP_LEFT = auto()
    TOP = auto()
    TOP_RIGHT = auto()
    LEFT = auto()
    RIGHT = auto()
    BOTTOM_LEFT = auto()
    BOTTOM = auto()
    BOTTOM_RIGHT = auto()

    def get_polygon(self, screen):
        size = 500
        w = screen.size().width()
        h = screen.size().height()
        match self:
            case ScreenEdge.TOP_LEFT:
                return QPolygonF(QRectF(-size, -size, size, size))
            case ScreenEdge.TOP:
                return QPolygonF(QRectF(    0, -size,    w, size))
            case ScreenEdge.TOP_RIGHT:
                return QPolygonF(QRectF(    w, -size, size, size))
            case ScreenEdge.LEFT:
                return QPolygonF(QRectF(-size,     0, size,    h))
            case ScreenEdge.RIGHT:
                return QPolygonF(QRectF(    w,     0, size,    h))
            case ScreenEdge.BOTTOM_LEFT:
                return QPolygonF(QRectF(-size,     h, size, size))
            case ScreenEdge.BOTTOM:
                return QPolygonF(QRectF(    0,     h,    w, size))
            case ScreenEdge.BOTTOM_RIGHT:
                return QPolygonF(QRectF(    w,     h, size, size))

    def __str__(self):
        return self.name.replace('_', ' ').title()

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
    friendly_name = 'Do Nothing'


class LogAction(Action):
    friendly_name = 'Log'

    def __init__(self):
        super().__init__()
        self._message = 'FLAG'

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value):
        self._message = value
        self.changed.emit()

    def execute(self, trigger_event):
        print('Log action:', self._message)


class ScrollAction(Action):
    friendly_name = 'Scroll'

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
    friendly_name = 'Hide Keyboard'

    def execute(self, trigger_event):
        QApplication.instance().main_window.keyboard.toggleKeyboard(False)

class ShowKeyboardAction(Action):
    friendly_name = 'Show Keyboard'

    def execute(self, trigger_event):
        QApplication.instance().main_window.keyboard.toggleKeyboard(True)

class ToggleKeyboardAction(Action):
    friendly_name = 'Toggle Keyboard'

    def execute(self, trigger_event):
        QApplication.instance().main_window.keyboard.toggleKeyboard()

class ToggleSettingsWindowAction(Action):
    friendly_name = 'Toggle Settings Window'

    def execute(self, trigger_event):
        QApplication.instance().toggle_settings_window()

class ToggleDebugWindowAction(Action):
    friendly_name = 'Toggle Debug Window'

    def execute(self, trigger_event):
        QApplication.instance().toggle_debug_window()

