# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'AboutDialog.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QFormLayout, QLabel,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(474, 234)
        Dialog.setModal(True)
        self.formLayout = QFormLayout(Dialog)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setContentsMargins(50, 50, 50, 9)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        font = QFont()
        font.setBold(True)
        self.label.setFont(font)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label)

        self.fmpyVersionLabel = QLabel(Dialog)
        self.fmpyVersionLabel.setObjectName(u"fmpyVersionLabel")
        self.fmpyVersionLabel.setFont(font)
        self.fmpyVersionLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.fmpyVersionLabel)

        self.label_10 = QLabel(Dialog)
        self.label_10.setObjectName(u"label_10")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_10)

        self.fmiPlatformLabel = QLabel(Dialog)
        self.fmiPlatformLabel.setObjectName(u"fmiPlatformLabel")
        self.fmiPlatformLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.fmiPlatformLabel)

        self.label_6 = QLabel(Dialog)
        self.label_6.setObjectName(u"label_6")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_6)

        self.installationPathLabel = QLabel(Dialog)
        self.installationPathLabel.setObjectName(u"installationPathLabel")
        self.installationPathLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.installationPathLabel)

        self.label_4 = QLabel(Dialog)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(4, QFormLayout.LabelRole, self.label_4)

        self.pythonInterpreterLabel = QLabel(Dialog)
        self.pythonInterpreterLabel.setObjectName(u"pythonInterpreterLabel")
        self.pythonInterpreterLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.pythonInterpreterLabel)

        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.formLayout.setWidget(6, QFormLayout.LabelRole, self.label_2)

        self.pythonVersionLabel = QLabel(Dialog)
        self.pythonVersionLabel.setObjectName(u"pythonVersionLabel")
        self.pythonVersionLabel.setWordWrap(True)
        self.pythonVersionLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.formLayout.setWidget(6, QFormLayout.FieldRole, self.pythonVersionLabel)

        self.verticalSpacer = QSpacerItem(20, 60, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.formLayout.setItem(8, QFormLayout.FieldRole, self.verticalSpacer)

        self.label_8 = QLabel(Dialog)
        self.label_8.setObjectName(u"label_8")

        self.formLayout.setWidget(9, QFormLayout.FieldRole, self.label_8)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"About FMPy", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"FMPy Version", None))
        self.fmpyVersionLabel.setText(QCoreApplication.translate("Dialog", u"2.0.0", None))
        self.label_10.setText(QCoreApplication.translate("Dialog", u"FMI Platform", None))
        self.fmiPlatformLabel.setText(QCoreApplication.translate("Dialog", u"win64", None))
        self.label_6.setText(QCoreApplication.translate("Dialog", u"Installation Path", None))
        self.installationPathLabel.setText(QCoreApplication.translate("Dialog", u"C:\\Anaconda3\\lib\\site-packages\\fmpy", None))
        self.label_4.setText(QCoreApplication.translate("Dialog", u"Python Interpreter", None))
        self.pythonInterpreterLabel.setText(QCoreApplication.translate("Dialog", u"C:\\Anaconda3\\python.exe", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Python Version", None))
        self.pythonVersionLabel.setText(QCoreApplication.translate("Dialog", u"3.5.2 |Anaconda custom (64-bit)| (default, Jul  5 2016, 11:41:13) [MSC v.1900 64 bit (AMD64)]", None))
        self.label_8.setText(QCoreApplication.translate("Dialog", u"\u00a9 2025 Dassault Syst\u00e8mes. All rights reserved.", None))
    # retranslateUi

