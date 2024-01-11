from PySide6.QtCore import (
    Signal,
    QTimer
)

from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QWidget,
    QLabel,
    QPushButton,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QStackedLayout,
    QHBoxLayout,
    QComboBox,
    QToolButton,
)

from pupil_labs.realtime_api.simple import discover_devices


class DeviceSettingsWidget(QWidget):
    def __init__(self):
        super().__init__()
        current_info = QWidget()
        current_info.setLayout(QFormLayout())
        current_info.layout().setHorizontalSpacing(20)


        self.device_ip_label = QLabel()
        current_info.layout().addRow("IP", self.device_ip_label)

        self.device_port_label = QLabel()
        current_info.layout().addRow("Port", self.device_port_label)

        self.disconnect_button = QPushButton("Disconnect")
        #self.disconnect_button.clicked.connect(app.companion.disconnect_device)

        self.connect_form = QWidget()
        self.connect_form.setLayout(QFormLayout())

        self.device_combo = DeviceCombo()
        self.device_combo.manual_entry_selected.connect(self.on_manual_entry_selected)
        self.device_combo.device_selected.connect(self.on_device_selected)
        self.device_combo.search_started.connect(lambda: self.setEnabled(False))
        self.device_combo.search_finished.connect(lambda: self.setEnabled(True))

        self.manual_host = QLineEdit()
        self.manual_host.setText("neon.local")

        self.manual_port = QSpinBox()
        self.manual_port.setRange(1, 65536)
        self.manual_port.setValue(8080)

        self.connect_form.layout().addRow("Device", self.device_combo)
        self.connect_form.layout().addRow("Host/IP", self.manual_host)
        self.connect_form.layout().addRow("Port", self.manual_port)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.connect_to_device)

        connected_page = QWidget()
        connected_page.setLayout(QVBoxLayout())
        connected_page.layout().addWidget(QLabel("<center><b>Connected!</b></center>"))
        connected_page.layout().addWidget(current_info)
        connected_page.layout().addStretch(1)
        connected_page.layout().addWidget(self.disconnect_button)

        disconnected_page = QWidget()
        disconnected_page.setLayout(QVBoxLayout())
        disconnected_page.layout().addWidget(QLabel("<center><b>Connect to Device</b></center>"))
        disconnected_page.layout().addWidget(self.connect_form)
        disconnected_page.layout().addStretch(1)
        disconnected_page.layout().addWidget(self.connect_button)

        self.setLayout(QStackedLayout())
        self.layout().addWidget(disconnected_page)
        self.layout().addWidget(connected_page)

        QTimer.singleShot(100, self.device_combo.initiate_refresh)


    def show(self):
        super().show()
        self.raise_()

        if self.pager.currentIndex() == 0:
            QTimer.singleShot(1, lambda: self.connect_button.setFocus())
        else:
            QTimer.singleShot(1, lambda: self.disconnect_button.setFocus())


    def connect_to_device(self):
        self.connect_button.setEnabled(False)
        self.connect_button.setText("Connecting...")

        app = QApplication.instance()
        if app.connect_to_device(self.manual_host.text(), self.manual_port.value()):
            self.layout().setCurrentIndex(1)
            self.device_ip_label.setText(self.manual_host.text())
            self.device_port_label.setText(str(self.manual_port.value()))

    def on_manual_entry_selected(self):
        self.manual_host.setEnabled(True)
        self.manual_port.setEnabled(True)


    def on_device_selected(self, device_info):
        self.manual_host.setEnabled(False)
        self.manual_host.setText(device_info["phone_ip"])

        self.manual_port.setEnabled(False)
        self.manual_port.setValue(device_info["port"])


class DeviceCombo(QWidget):
    manual_entry_selected = Signal()
    device_selected = Signal(object)
    search_started = Signal()
    search_finished = Signal()

    def __init__(self):
        super().__init__()

        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)

        self.combo = QComboBox()
        self.combo.addItem("Manual Entry")

        self.refresh_button = QToolButton()
        self.refresh_button.setText("🔍")
        self.refresh_button.clicked.connect(self.initiate_refresh)

        self.layout().addWidget(self.combo)
        self.layout().addWidget(self.refresh_button)

        self.combo.currentIndexChanged.connect(self.on_index_changed)

    def initiate_refresh(self):
        self.combo.clear()
        self.combo.addItem("Searching...")
        self.search_started.emit()
        QApplication.instance().processEvents()

        devices = discover_devices(search_duration_seconds=0.5)
        
        self.combo.clear()
        self.combo.addItem("Manual Entry")
        for device in devices:
            self.combo.addItem(
                f"{device.phone_name} ({device.dns_name})",
                {
                    "phone_ip": device.phone_ip,
                    "phone_name": device.phone_name,
                    "address": device.address,
                    "dns_name": device.dns_name,
                    "full_name": device.full_name,
                    "port": device.port,
                }
            )

        if len(devices) == 1:
            self.combo.setCurrentIndex(1)

        self.search_finished.emit()

    def on_index_changed(self, index):
        selected = self.combo.currentData()

        if selected is None:
            self.manual_entry_selected.emit()

        else:
            self.device_selected.emit(selected)
