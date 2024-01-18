from PySide6.QtCore import (
    Signal
)

from PySide6.QtWidgets import (
    QFormLayout,
    QLabel,
    QScrollArea,
    QTabWidget,
    QWidget,
)

from .property_widget import get_properties, create_property_widget, get_property_label
from .device_settings_widget import DeviceSettingsWidget

class SettingsWidget(QTabWidget):
    setting_changed = Signal(str, str, object)

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)
        self.resize(600, 600)

        self.settings_objects = {}

        self.device_settings_widget = DeviceSettingsWidget()
        self.add_page(self.device_settings_widget, "Companion Device")

    def add_object_page(self, object_or_objects, title):
        page = QWidget()
        page.setLayout(QFormLayout())

        objects = object_or_objects
        if not isinstance(objects, list):
            objects = [objects]

        for obj in objects:
            props = get_properties(obj.__class__)
            for property_name, prop in props.items():
                widget = create_property_widget(prop)
                widget.set_value(prop.fget(obj))
                widget.value_changed.connect(lambda v, obj=obj, prop=prop: prop.fset(obj, v))
                widget.value_changed.connect(lambda v, obj=obj, prop=prop, prop_name=property_name: self.setting_changed.emit(title, prop_name, v))

                label = QLabel(get_property_label(prop))
                label.setWordWrap(True)
                page.layout().addRow(label, widget)


        self.add_page(page, title)

    def add_page(self, widget, title):
        scroll_area = QScrollArea()
        scroll_area.setWidget(widget)
        scroll_area.setWidgetResizable(True)

        self.addTab(scroll_area, title)
