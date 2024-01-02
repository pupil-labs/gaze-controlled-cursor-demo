import numpy as np
import math


class DwellDetector:
    def __init__(self, minimumDelayInSeconds, rangeInPixels):
        self.minimumDelay = minimumDelayInSeconds
        self.range = rangeInPixels
        self.points = np.empty(shape=[0, 3])

        self.inDwell = False
        self.dwellProcess = 0

    def setDuration(self, duration):
        self.minimumDelay = duration

    def setRange(self, rangeInPixels):
        self.range = rangeInPixels

    def addPoint(self, gaze, timestamp):
        if gaze is None:
            self.points = np.empty(shape=[0, 3])
            return 0

        x, y = gaze
        point = np.array([x, y, timestamp])
        self.points = np.append(self.points, [point], axis=0)

        self.points = self.points[
            self.points[:, 2] >= timestamp - self.minimumDelay - 0.1
        ]

        center = np.mean(self.points[:, :2], axis=0)
        distances = np.sqrt(np.sum(self.points[:, :2] - center, axis=1) ** 2)
        if np.max(distances) > self.range:
            self.points = np.empty(shape=[0, 3])

        if len(self.points) > 1:
            duration = self.points[-1, 2] - self.points[0, 2]
            self.dwellProcess = duration / self.minimumDelay
        else:
            self.dwellProcess = 0

        if self.dwellProcess >= 1.0:
            self.points = np.empty(shape=[0, 3])
            return 1.0
        else:
            return self.dwellProcess
