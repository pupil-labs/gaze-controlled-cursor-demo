import numpy as np
import math
from PySide6.QtCore import *


class DwellDetector(QObject):
    dwell_duration_changed = Signal(float)

    def __init__(self, dwell_duration, rangeInPixels):
        super().__init__()

        self.dwell_time = dwell_duration
        self.range = rangeInPixels
        self.points = np.empty(shape=[0, 3])

        self.inDwell = False
        self.dwellProcess = 0

    @property
    def dwell_time(self) -> float:
        """
        :min 0.1
        :max 5.0
        :step 0.1
        :page_step 1.0
        """
        return self._dwell_time

    @dwell_time.setter
    def dwell_time(self, value):
        self._dwell_time = value
        self.dwell_duration_changed.emit(value)

    def addPoint(self, gaze, timestamp):
        if gaze is None:
            self.points = np.empty(shape=[0, 3])
            return 0

        x, y = gaze
        point = np.array([x, y, timestamp])
        self.points = np.append(self.points, [point], axis=0)

        self.points = self.points[
            self.points[:, 2] >= timestamp - self.dwell_time - 0.1
        ]

        center = np.mean(self.points[:, :2], axis=0)
        distances = np.sqrt(np.sum(self.points[:, :2] - center, axis=1) ** 2)
        if np.max(distances) > self.range:
            self.points = np.empty(shape=[0, 3])

        if len(self.points) > 1:
            duration = self.points[-1, 2] - self.points[0, 2]
            self.dwellProcess = duration / self.dwell_time
        else:
            self.dwellProcess = 0

        if self.dwellProcess >= 1.0:
            self.points = np.empty(shape=[0, 3])
            return 1.0
        else:
            return self.dwellProcess
