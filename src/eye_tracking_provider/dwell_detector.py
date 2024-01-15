import numpy as np
import math
from PySide6.QtCore import *


class DwellDetector(QObject):
    changed = Signal()
    dwell_duration_changed = Signal(float)

    def __init__(self):
        super().__init__()

        self._refractory_period = 1.5
        self._dwell_time = 1.0
        self._range = 75

        self.points = np.empty(shape=[0, 3])

        self.in_dwell = False
        self.dwell_process = 0
        self.last_dwell_timestamp = 0

    @property
    def dwell_time(self) -> float:
        """
        :min 0.25
        :max 5.0
        :step 0.25
        :page_step 1.0
        :decimals 2
        """
        return self._dwell_time

    @dwell_time.setter
    def dwell_time(self, value):
        self._dwell_time = value
        self.dwell_duration_changed.emit(value)
        self.changed.emit()

    @property
    def range(self) -> int:
        """
        :label Dwell Range (pixels)
        :min 1
        :max 500
        """
        return self._range

    @range.setter
    def range(self, value):
        self._range = value
        self.changed.emit()

    @property
    def refractory_period(self) -> float:
        """
        :min 0.0
        :max 30.0
        :decimals 2
        """
        return self._refractory_period

    @refractory_period.setter
    def refractory_period(self, value):
        self._refractory_period = value
        self.changed.emit()

    def addPoint(self, gaze, timestamp):
        if gaze is None:
            self.points = np.empty(shape=[0, 3])
            return 0

        if timestamp - self.last_dwell_timestamp < self._refractory_period:
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
            self.dwell_process = duration / self.dwell_time
        else:
            self.dwell_process = 0

        if self.dwell_process >= 1.0:
            self.last_dwell_timestamp = timestamp
            self.points = np.empty(shape=[0, 3])
            return 1.0
        else:
            return self.dwell_process

