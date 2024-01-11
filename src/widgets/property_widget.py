import typing
from enum import Enum

from PySide6.QtCore import (
    Qt,
    QTimer,
    Signal,
)

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QCheckBox,
    QComboBox,
    QLineEdit,
    QSlider,
    QPushButton,
    QGridLayout,
)


def create_property_widget(prop):
    hints = typing.get_type_hints(prop.fget)

    type_hint = str
    if 'return' in hints:
        type_hint = hints['return']

    property_doc = PropertyDocumentation(prop)
    widget = None

    if type_hint == bool:
        widget = QCheckBox()
        widget.set_value = widget.setChecked
        widget.get_value = widget.isChecked
        widget.value_changed = widget.stateChanged

    elif type_hint in [int, float]:
        widget = Slider()

        if 'min' in property_doc.hints:
            widget.set_minimum(float(property_doc.hints['min']))

        if 'max' in property_doc.hints:
            widget.set_maximum(float(property_doc.hints['max']))

        if 'step' in property_doc.hints:
            widget.set_step(float(property_doc.hints['step']))

        if 'page_step' in property_doc.hints:
            widget.set_page_size(float(property_doc.hints['page_step']))

        if type_hint == float:
            if 'decimals' in property_doc.hints:
                widget.set_decimals(int(property_doc.hints['decimals']))
            else:
                widget.set_decimals(3)

    elif issubclass(type_hint, Enum):
        widget = EnumCombo(type_hint)

    else:
        widget = QLineEdit()
        widget.set_value = widget.setText
        widget.get_value = widget.text
        widget.value_changed = widget.textChanged

    widget.setToolTip(property_doc.shortDescription)

    return widget

def get_class_properties(cls: type):
	properties = {}
	for key, value in cls.__dict__.items():
		if isinstance(value, property):
			properties[key] = value

	return properties

def get_properties(cls: type):
	properties = {}
	for kls in reversed(cls.mro()):
		class_props = get_class_properties(kls)
		for prop_name, prop in class_props.items():
			properties[prop_name] = prop

	return properties


class PropertyDocumentation():
    def __init__(self, prop):
        self.shortDescription = ''
        self.longDescription = ''
        self.hints = {}

        if prop.fget.__doc__ is None:
            return

        lines = []
        lineIdx = -1
        for line in prop.fget.__doc__.strip().split('\n'):
            line = line.strip()
            if len(line) > 0:
                lineIdx += 1
                if lineIdx == 0 and not line.startswith(':'):
                    self.shortDescription = line
                else:
                    lines.append(line)

        if len(lines) == 0:
            return

        for line in lines:
            if line.startswith(':'):
                left, right = line.split(maxsplit=1)
                self.hints[left[1:]] = right

            else:
                self.longDescription += '\n' + line

        self.longDescription = self.longDescription.strip()


class EnumCombo(QComboBox):
    value_changed = Signal(object)

    def __init__(self, enumClass):
        super().__init__()

        for e in enumClass:
            label = str(e)

            if label == f'{enumClass.__name__}.{e.name}':
                label = e.name.replace('_', ' ').title()

            self.addItem(label, e)

        self.currentIndexChanged.connect(self.onIndexChanged)

    def get_value(self):
        return self.currentData()

    def set_value(self, value):
        self.setCurrentIndex(self.findData(value))

    def onIndexChanged(self, idx):
        self.valueChanged.emit(self.currentData())


class Slider(QWidget):
    value_changed = Signal(float)

    def __init__(self):
        super().__init__()

        self.adjust_timer = QTimer()
        self.adjust_timer.timeout.connect(self._adjust)

        self.adjust_delta = 0

        self.setLayout(QGridLayout())
        self.setStyleSheet("QPushButton { font-size: 16pt; }")
        
        self.decrement_button = QPushButton("-")
        self.decrement_button.setText("-")
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.slider = QSlider(Qt.Horizontal)
        self.increment_button = QPushButton("+")

        self.decrement_button.pressed.connect(lambda: self._start_adjust(-1))
        self.increment_button.pressed.connect(lambda: self._start_adjust(1))
        self.decrement_button.released.connect(self.adjust_timer.stop)
        self.increment_button.released.connect(self.adjust_timer.stop)

        self.slider.valueChanged.connect(self._on_slider_value_changed)

        self.layout().addWidget(self.decrement_button, 0, 0, 2, 1)
        self.layout().addWidget(self.label, 0, 1, 1, 1)
        self.layout().addWidget(self.slider, 1, 1, 1, 1)
        self.layout().addWidget(self.increment_button, 0, 2, 2, 1)

        self._decimals = 0
        self._minimum = 0
        self._maximum = 99
        self._step_size = 1
        self._page_size = 10

    def set_minimum(self, value):
        self._minimum = value
        self._update_range()

    def set_maximum(self, value):
        self._maximum = value
        self._update_range()

    def set_decimals(self, decimals):
        self._decimals = decimals
        self._update_range()

    def _update_range(self):
        v = self.get_value()
        m = 10**self._decimals
        self.slider.setRange(
            self._minimum * m,
            self._maximum * m,
        )
        self.slider.setSingleStep(self._step_size * m)
        self.slider.setPageStep(self._page_size * m)
        self.slider.setValue(v * m)

    def set_step(self, step_size):
        self._step_size = step_size
        self.slider.setSingleStep(self._step_size * (10**self._decimals))

    def set_page_size(self, page_size):
        self._page_size = page_size
        self.slider.setPageStep(self._page_size * (10**self._decimals))

    def _start_adjust(self, delta):
        self.adjust_delta = delta
        self.slider.setValue(self.slider.value() + self.adjust_delta * self.slider.singleStep())

        self.adjust_timer.setInterval(1000)
        self.adjust_timer.start()

    def _adjust(self):
        self.slider.setValue(self.slider.value() + self.adjust_delta * self.slider.singleStep())
        self.adjust_timer.setInterval(25)

    def _on_slider_value_changed(self, value):
        if self._decimals > 0:
            value = round(value / (10**self._decimals), self._decimals)

        fstring = f"%0.{self._decimals}f"
        self.label.setText(fstring % value)
        self.value_changed.emit(value)

    def get_value(self):
        return self.slider.value() / (10**self._decimals)

    def set_value(self, v):
        self.slider.setValue(v * (10**self._decimals))
