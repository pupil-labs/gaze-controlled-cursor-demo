# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings.ui'
##
## Created by: Qt User Interface Compiler version 6.6.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QDialog, QFormLayout,
    QGroupBox, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QSlider, QWidget)

class Ui_Settings(object):
    def setupUi(self, Settings):
        if not Settings.objectName():
            Settings.setObjectName(u"Settings")
        Settings.resize(400, 275)
        self.groupBox = QGroupBox(Settings)
        self.groupBox.setObjectName(u"groupBox")
        self.groupBox.setGeometry(QRect(20, 30, 361, 171))
        self.widget = QWidget(self.groupBox)
        self.widget.setObjectName(u"widget")
        self.widget.setGeometry(QRect(10, 30, 341, 108))
        self.formLayout_2 = QFormLayout(self.widget)
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.widget)
        self.label_3.setObjectName(u"label_3")

        self.formLayout_2.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.device_ip = QLineEdit(self.widget)
        self.device_ip.setObjectName(u"device_ip")
        self.device_ip.setEnabled(False)

        self.formLayout_2.setWidget(2, QFormLayout.FieldRole, self.device_ip)

        self.device_status = QLabel(self.widget)
        self.device_status.setObjectName(u"device_status")

        self.formLayout_2.setWidget(0, QFormLayout.FieldRole, self.device_status)

        self.label_4 = QLabel(self.widget)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_2.setWidget(0, QFormLayout.LabelRole, self.label_4)

        self.device_connect_button = QPushButton(self.widget)
        self.device_connect_button.setObjectName(u"device_connect_button")
        self.device_connect_button.setEnabled(True)
        self.device_connect_button.setCheckable(False)

        self.formLayout_2.setWidget(4, QFormLayout.FieldRole, self.device_connect_button)

        self.device_auto_discovery = QCheckBox(self.widget)
        self.device_auto_discovery.setObjectName(u"device_auto_discovery")
        self.device_auto_discovery.setChecked(True)

        self.formLayout_2.setWidget(4, QFormLayout.LabelRole, self.device_auto_discovery)

        self.label_5 = QLabel(self.widget)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_2.setWidget(3, QFormLayout.LabelRole, self.label_5)

        self.port = QLineEdit(self.widget)
        self.port.setObjectName(u"port")
        self.port.setEnabled(False)

        self.formLayout_2.setWidget(3, QFormLayout.FieldRole, self.port)

        self.layoutWidget = QWidget(Settings)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.layoutWidget.setGeometry(QRect(20, 210, 361, 44))
        self.formLayout = QFormLayout(self.layoutWidget)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.layoutWidget)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.marker_brightness = QSlider(self.layoutWidget)
        self.marker_brightness.setObjectName(u"marker_brightness")
        self.marker_brightness.setMaximum(255)
        self.marker_brightness.setValue(128)
        self.marker_brightness.setOrientation(Qt.Horizontal)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.marker_brightness)

        self.label_2 = QLabel(self.layoutWidget)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_2)

        self.dwell_time = QSlider(self.layoutWidget)
        self.dwell_time.setObjectName(u"dwell_time")
        self.dwell_time.setMaximum(3000)
        self.dwell_time.setSingleStep(1)
        self.dwell_time.setValue(1000)
        self.dwell_time.setOrientation(Qt.Horizontal)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.dwell_time)


        self.retranslateUi(Settings)

        QMetaObject.connectSlotsByName(Settings)
    # setupUi

    def retranslateUi(self, Settings):
        Settings.setWindowTitle(QCoreApplication.translate("Settings", u"Dialog", None))
        self.groupBox.setTitle(QCoreApplication.translate("Settings", u"Neon Device", None))
        self.label_3.setText(QCoreApplication.translate("Settings", u"IP:", None))
        self.device_ip.setText(QCoreApplication.translate("Settings", u"n/A", None))
        self.device_status.setText(QCoreApplication.translate("Settings", u"Not connected", None))
        self.label_4.setText(QCoreApplication.translate("Settings", u"Status:", None))
        self.device_connect_button.setText(QCoreApplication.translate("Settings", u"Connect", None))
        self.device_auto_discovery.setText(QCoreApplication.translate("Settings", u"Auto Discover", None))
        self.label_5.setText(QCoreApplication.translate("Settings", u"Port", None))
        self.port.setText(QCoreApplication.translate("Settings", u"8080", None))
        self.label.setText(QCoreApplication.translate("Settings", u"Marker Brightness", None))
        self.label_2.setText(QCoreApplication.translate("Settings", u"Dwell Time", None))
    # retranslateUi

