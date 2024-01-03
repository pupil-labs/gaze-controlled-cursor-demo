from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import *


def map_rect_to_global(widget):
    rect = widget.rect()
    x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
    p = widget.mapToGlobal(QPoint(x, y))
    x, y = p.x(), p.y()
    return QRect(x, y, w, h)
