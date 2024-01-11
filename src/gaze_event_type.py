from enum import Enum, auto

class GazeEventType(Enum):
    GAZE_ENTER = auto()
    GAZE_EXIT = auto()
    GAZE_UPON = auto()
    FIXATE = auto()

class TriggerEvent:
    def __init__(self, event_config, gaze_data):
        self.event_config = event_config
        self.gaze_data = gaze_data
