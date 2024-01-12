from PySide6.QtGui import QImage


def qimage_from_frame(frame, format=None):
    if frame is None:
        return QImage()

    if len(frame.shape) == 2:
        height, width = frame.shape
        channel = 1
        image_format = QImage.Format_Grayscale8
    else:
        height, width, channel = frame.shape
        image_format = QImage.Format_BGR888

    if format is not None:
        image_format = format

    bytes_per_line = channel * width

    return QImage(frame.data, width, height, bytes_per_line, image_format)
