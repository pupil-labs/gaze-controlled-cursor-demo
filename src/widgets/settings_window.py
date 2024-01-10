from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from .ui.settings import Ui_Settings


class SettingsWindow(QWidget, Ui_Settings):
    device_connection_request = Signal(bool, str, int)

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.setupUi(self)

        # Setup internal signals
        self.device_auto_discovery.stateChanged.connect(self.on_device_auto_discovery)
        self.device_connect_button.clicked.connect(
            self.on_device_connect_button_clicked
        )

        # Connect signals to controller
        self.device_connection_request.connect(self.controller.connect_to_device)

        # marker_brightness
        self.marker_brightness.valueChanged.connect(
            self.controller.main_window.marker_overlay.set_brightness
        )

        # dwell_time
        self.dwell_time.valueChanged.connect(
            lambda v: self.controller.eye_tracking_provider.dwell_detector.__setattr__(
                "dwell_time", v / 1000
            )
        )
        self.controller.eye_tracking_provider.dwell_detector.dwell_duration_changed.connect(
            lambda v: self.dwell_time.setValue(v * 1000)
        )

    def on_dwell_duration_changed(self, value):
        self.dwell_time.setValue(value)

    def on_device_auto_discovery(self, value):
        self.device_ip.setEnabled(not value)
        self.port.setEnabled(not value)

    def on_device_connect_button_clicked(self):
        # TODO: Why does the text change not come through?
        self.device_status.setText("Connecting...")
        self.device_connection_request.emit(
            self.device_auto_discovery.isChecked(),
            self.device_ip.text(),
            int(self.port.text()),
        )

    def on_connection_attempt(self, ip, port, status):
        if ip is not None:
            self.device_ip.setText(ip)
        if port is not None:
            self.port.setText(str(port))
        if status is not None:
            self.device_status.setText(status)
