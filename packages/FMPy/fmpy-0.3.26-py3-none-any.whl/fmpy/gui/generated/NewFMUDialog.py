# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'NewFMUDialog.ui'
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
    QSpinBox, QToolButton, QWidget)

class Ui_NewFMUDialog(object):
    def setupUi(self, NewFMUDialog):
        if not NewFMUDialog.objectName():
            NewFMUDialog.setObjectName(u"NewFMUDialog")
        NewFMUDialog.resize(409, 360)
        self.gridLayout = QGridLayout(NewFMUDialog)
        self.gridLayout.setSpacing(12)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(12, 12, 12, 12)
        self.label = QLabel(NewFMUDialog)
        self.label.setObjectName(u"label")

        self.gridLayout.addWidget(self.label, 3, 0, 1, 2)

        self.widget = QWidget(NewFMUDialog)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.filenameLineEdit = QLineEdit(self.widget)
        self.filenameLineEdit.setObjectName(u"filenameLineEdit")

        self.horizontalLayout.addWidget(self.filenameLineEdit)

        self.selectFilenameButton = QToolButton(self.widget)
        self.selectFilenameButton.setObjectName(u"selectFilenameButton")

        self.horizontalLayout.addWidget(self.selectFilenameButton)


        self.gridLayout.addWidget(self.widget, 1, 2, 1, 2)

        self.label_6 = QLabel(NewFMUDialog)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 1)

        self.label_5 = QLabel(NewFMUDialog)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout.addWidget(self.label_5, 1, 0, 1, 1)

        self.nInputsSpinBox = QSpinBox(NewFMUDialog)
        self.nInputsSpinBox.setObjectName(u"nInputsSpinBox")
        self.nInputsSpinBox.setMaximum(100000)
        self.nInputsSpinBox.setValue(5)

        self.gridLayout.addWidget(self.nInputsSpinBox, 4, 2, 1, 1)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout.addItem(self.verticalSpacer, 8, 0, 1, 4)

        self.nOutputsSpinBox = QSpinBox(NewFMUDialog)
        self.nOutputsSpinBox.setObjectName(u"nOutputsSpinBox")
        self.nOutputsSpinBox.setMaximum(100000)
        self.nOutputsSpinBox.setValue(5)

        self.gridLayout.addWidget(self.nOutputsSpinBox, 5, 2, 1, 1)

        self.nLocalVariablesSpinBox = QSpinBox(NewFMUDialog)
        self.nLocalVariablesSpinBox.setObjectName(u"nLocalVariablesSpinBox")
        self.nLocalVariablesSpinBox.setMaximum(100000)
        self.nLocalVariablesSpinBox.setValue(5)

        self.gridLayout.addWidget(self.nLocalVariablesSpinBox, 6, 2, 1, 1)

        self.label_4 = QLabel(NewFMUDialog)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout.addWidget(self.label_4, 6, 0, 1, 2)

        self.buttonBox = QDialogButtonBox(NewFMUDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.gridLayout.addWidget(self.buttonBox, 9, 0, 1, 4)

        self.label_3 = QLabel(NewFMUDialog)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 2)

        self.label_2 = QLabel(NewFMUDialog)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 2)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 2, 3, 1, 1)

        self.fmiVersionComboBox = QComboBox(NewFMUDialog)
        self.fmiVersionComboBox.addItem("")
        self.fmiVersionComboBox.addItem("")
        self.fmiVersionComboBox.setObjectName(u"fmiVersionComboBox")
        self.fmiVersionComboBox.setEnabled(False)

        self.gridLayout.addWidget(self.fmiVersionComboBox, 2, 2, 1, 1)

        self.nParametersSpinBox = QSpinBox(NewFMUDialog)
        self.nParametersSpinBox.setObjectName(u"nParametersSpinBox")
        self.nParametersSpinBox.setMaximum(100000)
        self.nParametersSpinBox.setValue(5)

        self.gridLayout.addWidget(self.nParametersSpinBox, 3, 2, 1, 1)

        self.openFMUCheckBox = QCheckBox(NewFMUDialog)
        self.openFMUCheckBox.setObjectName(u"openFMUCheckBox")
        self.openFMUCheckBox.setChecked(True)

        self.gridLayout.addWidget(self.openFMUCheckBox, 7, 0, 1, 4)


        self.retranslateUi(NewFMUDialog)
        self.buttonBox.accepted.connect(NewFMUDialog.accept)
        self.buttonBox.rejected.connect(NewFMUDialog.reject)

        QMetaObject.connectSlotsByName(NewFMUDialog)
    # setupUi

    def retranslateUi(self, NewFMUDialog):
        NewFMUDialog.setWindowTitle(QCoreApplication.translate("NewFMUDialog", u"Create a new FMU", None))
        self.label.setText(QCoreApplication.translate("NewFMUDialog", u"Parameters", None))
        self.filenameLineEdit.setText("")
        self.selectFilenameButton.setText(QCoreApplication.translate("NewFMUDialog", u"...", None))
        self.label_6.setText(QCoreApplication.translate("NewFMUDialog", u"FMI Version", None))
        self.label_5.setText(QCoreApplication.translate("NewFMUDialog", u"Filename", None))
        self.label_4.setText(QCoreApplication.translate("NewFMUDialog", u"Local Variables", None))
        self.label_3.setText(QCoreApplication.translate("NewFMUDialog", u"Outputs", None))
        self.label_2.setText(QCoreApplication.translate("NewFMUDialog", u"Inputs", None))
        self.fmiVersionComboBox.setItemText(0, QCoreApplication.translate("NewFMUDialog", u"3", None))
        self.fmiVersionComboBox.setItemText(1, QCoreApplication.translate("NewFMUDialog", u"2", None))

        self.openFMUCheckBox.setText(QCoreApplication.translate("NewFMUDialog", u"Open FMU", None))
    # retranslateUi

