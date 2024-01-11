from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from actions import EdgeActionConfig
from .property_widget import create_object_widget

class ActionSettingsWidget(QWidget):
    action_config_added = Signal(object)
    action_config_deleted = Signal(object)

    def __init__(self, action_configs=None):
        super().__init__()

        self.setLayout(QVBoxLayout())

        self.action_metas = []

        self.rows = QWidget()
        self.rows.setLayout(QGridLayout())

        self.add_button = QPushButton("Add action")
        self.add_button.clicked.connect(self._add_row)

        self.layout().addWidget(self.rows)
        self.layout().addStretch()
        self.layout().addWidget(self.add_button)

        for action_config in action_configs:
            self._add_action_config_row(action_config)


    def _add_row(self):
        action_config = EdgeActionConfig()
        self._add_action_config_row(action_config)
        self.action_config_added.emit(action_config)

    def _add_action_config_row(self, action_config):
        form = create_object_widget(action_config)

        row_idx = self.rows.layout().rowCount()
        self.rows.layout().addWidget(form, row_idx, 0)
