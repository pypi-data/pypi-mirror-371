# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'TableDialog.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QFrame, QGridLayout, QHeaderView,
    QRadioButton, QSizePolicy, QSpacerItem, QSplitter,
    QTableView, QVBoxLayout, QWidget)

from pyqtgraph import GraphicsLayoutWidget
from . import icons_rc

class Ui_TableDialog(object):
    def setupUi(self, TableDialog):
        if not TableDialog.objectName():
            TableDialog.setObjectName(u"TableDialog")
        TableDialog.resize(902, 561)
        self.verticalLayout_2 = QVBoxLayout(TableDialog)
        self.verticalLayout_2.setSpacing(15)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.splitter = QSplitter(TableDialog)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setStyleSheet(u"QSplitter::handle:horizontal {\n"
"	border-left: 1px solid #ccc;\n"
"}")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.tableView = QTableView(self.splitter)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setFrameShape(QFrame.Shape.NoFrame)
        self.splitter.addWidget(self.tableView)
        self.frame = QFrame(self.splitter)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.verticalLayout = QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, -1, 0, 0)
        self.plotSettingsWidget = QWidget(self.frame)
        self.plotSettingsWidget.setObjectName(u"plotSettingsWidget")
        self.gridLayout_2 = QGridLayout(self.plotSettingsWidget)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(20, -1, -1, -1)
        self.plotRowsRadioButton = QRadioButton(self.plotSettingsWidget)
        self.plotRowsRadioButton.setObjectName(u"plotRowsRadioButton")

        self.gridLayout_2.addWidget(self.plotRowsRadioButton, 1, 0, 1, 1)

        self.plotColumnsRadioButton = QRadioButton(self.plotSettingsWidget)
        self.plotColumnsRadioButton.setObjectName(u"plotColumnsRadioButton")
        self.plotColumnsRadioButton.setChecked(True)

        self.gridLayout_2.addWidget(self.plotColumnsRadioButton, 0, 0, 1, 1)

        self.firstColumnAsXAxisCheckBox = QCheckBox(self.plotSettingsWidget)
        self.firstColumnAsXAxisCheckBox.setObjectName(u"firstColumnAsXAxisCheckBox")
        self.firstColumnAsXAxisCheckBox.setChecked(True)

        self.gridLayout_2.addWidget(self.firstColumnAsXAxisCheckBox, 0, 1, 1, 1)

        self.firstRowAsXAxisCheckBox = QCheckBox(self.plotSettingsWidget)
        self.firstRowAsXAxisCheckBox.setObjectName(u"firstRowAsXAxisCheckBox")
        self.firstRowAsXAxisCheckBox.setEnabled(False)
        self.firstRowAsXAxisCheckBox.setChecked(True)

        self.gridLayout_2.addWidget(self.firstRowAsXAxisCheckBox, 1, 1, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 2, 1, 1)


        self.verticalLayout.addWidget(self.plotSettingsWidget)

        self.graphicsView = GraphicsLayoutWidget(self.frame)
        self.graphicsView.setObjectName(u"graphicsView")

        self.verticalLayout.addWidget(self.graphicsView)

        self.splitter.addWidget(self.frame)

        self.verticalLayout_2.addWidget(self.splitter)

        self.buttonBox = QDialogButtonBox(TableDialog)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout_2.addWidget(self.buttonBox)


        self.retranslateUi(TableDialog)
        self.buttonBox.accepted.connect(TableDialog.accept)
        self.buttonBox.rejected.connect(TableDialog.reject)
        self.plotColumnsRadioButton.toggled.connect(self.firstColumnAsXAxisCheckBox.setEnabled)
        self.plotRowsRadioButton.toggled.connect(self.firstRowAsXAxisCheckBox.setEnabled)

        QMetaObject.connectSlotsByName(TableDialog)
    # setupUi

    def retranslateUi(self, TableDialog):
        self.plotRowsRadioButton.setText(QCoreApplication.translate("TableDialog", u"Plot Rows", None))
        self.plotColumnsRadioButton.setText(QCoreApplication.translate("TableDialog", u"Plot Columns", None))
        self.firstColumnAsXAxisCheckBox.setText(QCoreApplication.translate("TableDialog", u"first column as x-axis", None))
        self.firstRowAsXAxisCheckBox.setText(QCoreApplication.translate("TableDialog", u"first row as x-axis", None))
        pass
    # retranslateUi

