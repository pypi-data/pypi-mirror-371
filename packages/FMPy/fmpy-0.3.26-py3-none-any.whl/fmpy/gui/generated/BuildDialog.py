# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'BuildDialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QSizePolicy, QSpacerItem,
    QToolButton, QWidget)

class Ui_BuildDialog(object):
    def setupUi(self, BuildDialog):
        if not BuildDialog.objectName():
            BuildDialog.setObjectName(u"BuildDialog")
        BuildDialog.resize(460, 298)
        self.gridLayout = QGridLayout(BuildDialog)
        self.gridLayout.setSpacing(12)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(12, 12, 12, 12)
        self.label_4 = QLabel(BuildDialog)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 0, 0, 1, 1)

        self.generatorComboBox = QComboBox(BuildDialog)
        self.generatorComboBox.setObjectName(u"generatorComboBox")

        self.gridLayout.addWidget(self.generatorComboBox, 2, 1, 1, 1)

        self.platformComboBox = QComboBox(BuildDialog)
        self.platformComboBox.setObjectName(u"platformComboBox")

        self.gridLayout.addWidget(self.platformComboBox, 3, 1, 1, 1)

        self.label_3 = QLabel(BuildDialog)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 8, 0, 1, 1)

        self.label_2 = QLabel(BuildDialog)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)

        self.allWarningsCheckBox = QCheckBox(BuildDialog)
        self.allWarningsCheckBox.setObjectName(u"allWarningsCheckBox")

        self.gridLayout.addWidget(self.allWarningsCheckBox, 5, 0, 1, 2)

        self.configurationComboBox = QComboBox(BuildDialog)
        self.configurationComboBox.setObjectName(u"configurationComboBox")

        self.gridLayout.addWidget(self.configurationComboBox, 4, 1, 1, 1)

        self.buttonBox = QDialogButtonBox(BuildDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 2)

        self.label = QLabel(BuildDialog)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)

        self.compileWithWslCheckBox = QCheckBox(BuildDialog)
        self.compileWithWslCheckBox.setObjectName(u"compileWithWslCheckBox")

        self.gridLayout.addWidget(self.compileWithWslCheckBox, 7, 0, 1, 2)

        self.widget = QWidget(BuildDialog)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.buildDirectoryLineEdit = QLineEdit(self.widget)
        self.buildDirectoryLineEdit.setObjectName(u"buildDirectoryLineEdit")

        self.horizontalLayout.addWidget(self.buildDirectoryLineEdit)

        self.selectBuildDirectoryToolButton = QToolButton(self.widget)
        self.selectBuildDirectoryToolButton.setObjectName(u"selectBuildDirectoryToolButton")

        self.horizontalLayout.addWidget(self.selectBuildDirectoryToolButton)


        self.gridLayout.addWidget(self.widget, 0, 1, 1, 1)

        self.warningAsErrorCheckBox = QCheckBox(BuildDialog)
        self.warningAsErrorCheckBox.setObjectName(u"warningAsErrorCheckBox")

        self.gridLayout.addWidget(self.warningAsErrorCheckBox, 6, 0, 1, 2)


        self.retranslateUi(BuildDialog)
        self.buttonBox.accepted.connect(BuildDialog.accept)
        self.buttonBox.rejected.connect(BuildDialog.reject)

        QMetaObject.connectSlotsByName(BuildDialog)
    # setupUi

    def retranslateUi(self, BuildDialog):
        BuildDialog.setWindowTitle(QCoreApplication.translate("BuildDialog", u"Build Platform Binary", None))
        self.label_4.setText(QCoreApplication.translate("BuildDialog", u"Build Directory", None))
        self.label_3.setText(QCoreApplication.translate("BuildDialog", u"Configuration", None))
        self.label_2.setText(QCoreApplication.translate("BuildDialog", u"Generator", None))
        self.allWarningsCheckBox.setText(QCoreApplication.translate("BuildDialog", u"Enable all compiler warnings", None))
        self.label.setText(QCoreApplication.translate("BuildDialog", u"Platform", None))
        self.compileWithWslCheckBox.setText(QCoreApplication.translate("BuildDialog", u"Compile for Linux with WSL", None))
        self.buildDirectoryLineEdit.setText("")
        self.buildDirectoryLineEdit.setPlaceholderText(QCoreApplication.translate("BuildDialog", u"Create temporary directory", None))
        self.selectBuildDirectoryToolButton.setText(QCoreApplication.translate("BuildDialog", u"...", None))
        self.warningAsErrorCheckBox.setText(QCoreApplication.translate("BuildDialog", u"Turn compiler warnings into errors", None))
    # retranslateUi

