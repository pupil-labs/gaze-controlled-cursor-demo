import numpy as np
import math

class DwellDetector():
    def __init__(self, minimumDelayInSeconds, rangeInPixels):
        self.minimumDelay = minimumDelayInSeconds
        self.range = rangeInPixels
        self.points = np.empty(shape=[0, 3])

        self.inDwell = False

    def setDuration(self, duration):
        self.minimumDelay = duration

    def setRange(self, rangeInPixels):
        self.range = rangeInPixels

    def addPoint(self, x, y, timestamp):
        point = np.array([x, y, timestamp])

        self.points = np.append(self.points, [point], axis=0)
        if self.points[-1,2] - self.points[0,2] < self.minimumDelay:
            return False, False, None

        minTimestamp = timestamp - self.minimumDelay - .0001
        self.points = self.points[self.points[:,2] >= minTimestamp]

        center = np.mean(self.points[:,:2], axis=0)
        distances = np.sqrt(np.sum(self.points[:,:2] - center, axis=1)**2)

        if np.max(distances) < self.range:
            inDwell = True
        else:
            inDwell = False

        changed = inDwell != self.inDwell
        self.inDwell = inDwell

        return changed, inDwell, center
