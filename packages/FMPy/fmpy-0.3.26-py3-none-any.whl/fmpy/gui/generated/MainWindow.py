# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindow.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QDockWidget, QFrame, QGraphicsView, QGridLayout,
    QGroupBox, QHBoxLayout, QHeaderView, QLabel,
    QLineEdit, QMainWindow, QMenu, QMenuBar,
    QPushButton, QRadioButton, QSizePolicy, QSpacerItem,
    QStackedWidget, QStatusBar, QToolBar, QToolButton,
    QTreeView, QVBoxLayout, QWidget)
from . import icons_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1125, 836)
        MainWindow.setAcceptDrops(True)
        icon = QIcon()
        icon.addFile(u":/icons/app_icon.ico", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        MainWindow.setStyleSheet(u"QToolBar::separator { width: 20px }")
        self.actionSimulate = QAction(MainWindow)
        self.actionSimulate.setObjectName(u"actionSimulate")
        icon1 = QIcon()
        icon1.addFile(u":/icons/dark/play.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionSimulate.setIcon(icon1)
        self.actionShowSettings = QAction(MainWindow)
        self.actionShowSettings.setObjectName(u"actionShowSettings")
        self.actionShowSettings.setCheckable(True)
        icon2 = QIcon()
        icon2.addFile(u":/icons/dark/gear.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionShowSettings.setIcon(icon2)
        self.actionOpen = QAction(MainWindow)
        self.actionOpen.setObjectName(u"actionOpen")
        icon3 = QIcon()
        icon3.addFile(u":/icons/dark/folder-open.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionOpen.setIcon(icon3)
        self.actionShowResults = QAction(MainWindow)
        self.actionShowResults.setObjectName(u"actionShowResults")
        self.actionShowResults.setCheckable(True)
        icon4 = QIcon()
        icon4.addFile(u":/icons/dark/graph.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionShowResults.setIcon(icon4)
        self.actionNewWindow = QAction(MainWindow)
        self.actionNewWindow.setObjectName(u"actionNewWindow")
        self.actionFilterInputs = QAction(MainWindow)
        self.actionFilterInputs.setObjectName(u"actionFilterInputs")
        self.actionFilterInputs.setCheckable(True)
        self.actionFilterInputs.setChecked(True)
        self.actionFilterOutputs = QAction(MainWindow)
        self.actionFilterOutputs.setObjectName(u"actionFilterOutputs")
        self.actionFilterOutputs.setCheckable(True)
        self.actionFilterOutputs.setChecked(True)
        self.actionFilterParameters = QAction(MainWindow)
        self.actionFilterParameters.setObjectName(u"actionFilterParameters")
        self.actionFilterParameters.setCheckable(True)
        self.actionFilterParameters.setChecked(True)
        self.actionFilterLocalVariables = QAction(MainWindow)
        self.actionFilterLocalVariables.setObjectName(u"actionFilterLocalVariables")
        self.actionFilterLocalVariables.setCheckable(True)
        self.actionFilterIndependentVariables = QAction(MainWindow)
        self.actionFilterIndependentVariables.setObjectName(u"actionFilterIndependentVariables")
        self.actionFilterIndependentVariables.setCheckable(True)
        self.actionFilterCalculatedParameters = QAction(MainWindow)
        self.actionFilterCalculatedParameters.setObjectName(u"actionFilterCalculatedParameters")
        self.actionFilterCalculatedParameters.setCheckable(True)
        self.actionOpenFMI2Spec = QAction(MainWindow)
        self.actionOpenFMI2Spec.setObjectName(u"actionOpenFMI2Spec")
        self.actionOpenFMI1SpecCS = QAction(MainWindow)
        self.actionOpenFMI1SpecCS.setObjectName(u"actionOpenFMI1SpecCS")
        self.actionOpenFMI1SpecME = QAction(MainWindow)
        self.actionOpenFMI1SpecME.setObjectName(u"actionOpenFMI1SpecME")
        self.actionClose = QAction(MainWindow)
        self.actionClose.setObjectName(u"actionClose")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionShowLog = QAction(MainWindow)
        self.actionShowLog.setObjectName(u"actionShowLog")
        self.actionShowLog.setCheckable(True)
        icon5 = QIcon()
        icon5.addFile(u":/icons/dark/list-task.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionShowLog.setIcon(icon5)
        self.actionOpenTestFMUs = QAction(MainWindow)
        self.actionOpenTestFMUs.setObjectName(u"actionOpenTestFMUs")
        self.actionSaveResult = QAction(MainWindow)
        self.actionSaveResult.setObjectName(u"actionSaveResult")
        self.actionSavePlottedResult = QAction(MainWindow)
        self.actionSavePlottedResult.setObjectName(u"actionSavePlottedResult")
        self.actionCreateDesktopShortcut = QAction(MainWindow)
        self.actionCreateDesktopShortcut.setObjectName(u"actionCreateDesktopShortcut")
        self.actionShowAboutDialog = QAction(MainWindow)
        self.actionShowAboutDialog.setObjectName(u"actionShowAboutDialog")
        self.actionOpenWebsite = QAction(MainWindow)
        self.actionOpenWebsite.setObjectName(u"actionOpenWebsite")
        self.actionAddFileAssociation = QAction(MainWindow)
        self.actionAddFileAssociation.setObjectName(u"actionAddFileAssociation")
        self.actionShowReleaseNotes = QAction(MainWindow)
        self.actionShowReleaseNotes.setObjectName(u"actionShowReleaseNotes")
        self.actionReload = QAction(MainWindow)
        self.actionReload.setObjectName(u"actionReload")
        icon6 = QIcon()
        icon6.addFile(u":/icons/dark/arrow-clockwise.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionReload.setIcon(icon6)
        self.actionSaveChanges = QAction(MainWindow)
        self.actionSaveChanges.setObjectName(u"actionSaveChanges")
        self.actionLoadStartValues = QAction(MainWindow)
        self.actionLoadStartValues.setObjectName(u"actionLoadStartValues")
        self.actionCreateCMakeProject = QAction(MainWindow)
        self.actionCreateCMakeProject.setObjectName(u"actionCreateCMakeProject")
        self.actionCreateCMakeProject.setEnabled(False)
        self.actionAddCoSimulationWrapper = QAction(MainWindow)
        self.actionAddCoSimulationWrapper.setObjectName(u"actionAddCoSimulationWrapper")
        self.actionAddCoSimulationWrapper.setEnabled(False)
        self.actionCreateJupyterNotebook = QAction(MainWindow)
        self.actionCreateJupyterNotebook.setObjectName(u"actionCreateJupyterNotebook")
        self.actionCreateJupyterNotebook.setEnabled(False)
        self.actionValidateFMU = QAction(MainWindow)
        self.actionValidateFMU.setObjectName(u"actionValidateFMU")
        self.actionValidateFMU.setEnabled(False)
        self.actionAddLinux64Remoting = QAction(MainWindow)
        self.actionAddLinux64Remoting.setObjectName(u"actionAddLinux64Remoting")
        self.actionAddLinux64Remoting.setEnabled(False)
        self.actionAddWindows32Remoting = QAction(MainWindow)
        self.actionAddWindows32Remoting.setObjectName(u"actionAddWindows32Remoting")
        self.actionAddWindows32Remoting.setEnabled(False)
        self.actionShowDocumentation = QAction(MainWindow)
        self.actionShowDocumentation.setObjectName(u"actionShowDocumentation")
        self.actionShowDocumentation.setCheckable(True)
        icon7 = QIcon()
        icon7.addFile(u":/icons/dark/book.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionShowDocumentation.setIcon(icon7)
        self.actionShowFiles = QAction(MainWindow)
        self.actionShowFiles.setObjectName(u"actionShowFiles")
        self.actionShowFiles.setCheckable(True)
        icon8 = QIcon()
        icon8.addFile(u":/icons/dark/file-earmark-zip.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionShowFiles.setIcon(icon8)
        self.actionOpenUnzipDirectory = QAction(MainWindow)
        self.actionOpenUnzipDirectory.setObjectName(u"actionOpenUnzipDirectory")
        self.actionRemoveSourceCode = QAction(MainWindow)
        self.actionRemoveSourceCode.setObjectName(u"actionRemoveSourceCode")
        self.actionRemoveSourceCode.setEnabled(False)
        self.actionOpenFMI3Spec = QAction(MainWindow)
        self.actionOpenFMI3Spec.setObjectName(u"actionOpenFMI3Spec")
        self.actionOpenFMI3Spec.setMenuRole(QAction.MenuRole.NoRole)
        self.actionShowNewFMUDialog = QAction(MainWindow)
        self.actionShowNewFMUDialog.setObjectName(u"actionShowNewFMUDialog")
        icon9 = QIcon()
        icon9.addFile(u":/icons/dark/file-new.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionShowNewFMUDialog.setIcon(icon9)
        self.actionBuildPlatformBinary = QAction(MainWindow)
        self.actionBuildPlatformBinary.setObjectName(u"actionBuildPlatformBinary")
        icon10 = QIcon()
        icon10.addFile(u":/icons/dark/hammer.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionBuildPlatformBinary.setIcon(icon10)
        self.actionBuildPlatformBinary.setMenuRole(QAction.MenuRole.NoRole)
        self.actionSave = QAction(MainWindow)
        self.actionSave.setObjectName(u"actionSave")
        icon11 = QIcon()
        icon11.addFile(u":/icons/dark/floppy.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionSave.setIcon(icon11)
        self.actionSaveAs = QAction(MainWindow)
        self.actionSaveAs.setObjectName(u"actionSaveAs")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout_12 = QHBoxLayout(self.centralwidget)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.startPage = QWidget()
        self.startPage.setObjectName(u"startPage")
        self.verticalLayout_2 = QVBoxLayout(self.startPage)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalSpacer_4 = QSpacerItem(20, 100, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer_4)

        self.verticalSpacer_2 = QSpacerItem(20, 113, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.widget_8 = QWidget(self.startPage)
        self.widget_8.setObjectName(u"widget_8")
        self.horizontalLayout_7 = QHBoxLayout(self.widget_8)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_2.addWidget(self.widget_8)

        self.widget_9 = QWidget(self.startPage)
        self.widget_9.setObjectName(u"widget_9")
        self.horizontalLayout_8 = QHBoxLayout(self.widget_9)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_9 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_9)

        self.label_11 = QLabel(self.widget_9)
        self.label_11.setObjectName(u"label_11")

        self.horizontalLayout_8.addWidget(self.label_11)

        self.openButton = QPushButton(self.widget_9)
        self.openButton.setObjectName(u"openButton")
        icon12 = QIcon(QIcon.fromTheme(u"folder-open"))
        self.openButton.setIcon(icon12)

        self.horizontalLayout_8.addWidget(self.openButton)

        self.horizontalSpacer_10 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_10)


        self.verticalLayout_2.addWidget(self.widget_9)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.widget = QWidget(self.startPage)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(0, 20))
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.recentFilesGroupBox = QGroupBox(self.widget)
        self.recentFilesGroupBox.setObjectName(u"recentFilesGroupBox")
        self.recentFilesGroupBox.setMinimumSize(QSize(200, 0))
        self.recentFilesGroupBox.setFlat(True)

        self.horizontalLayout.addWidget(self.recentFilesGroupBox)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)


        self.verticalLayout_2.addWidget(self.widget)

        self.verticalSpacer_3 = QSpacerItem(20, 112, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_3)

        self.stackedWidget.addWidget(self.startPage)
        self.settingsPage = QWidget()
        self.settingsPage.setObjectName(u"settingsPage")
        self.verticalLayout = QVBoxLayout(self.settingsPage)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        self.infoGroupBox = QGroupBox(self.settingsPage)
        self.infoGroupBox.setObjectName(u"infoGroupBox")
        self.infoGroupBox.setFlat(True)
        self.gridLayout_9 = QGridLayout(self.infoGroupBox)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setHorizontalSpacing(9)
        self.gridLayout_9.setVerticalSpacing(12)
        self.gridLayout_9.setContentsMargins(-1, 12, -1, -1)
        self.modelNameLabel = QLabel(self.infoGroupBox)
        self.modelNameLabel.setObjectName(u"modelNameLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.modelNameLabel.sizePolicy().hasHeightForWidth())
        self.modelNameLabel.setSizePolicy(sizePolicy)
        self.modelNameLabel.setWordWrap(True)
        self.modelNameLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_9.addWidget(self.modelNameLabel, 2, 1, 1, 1)

        self.label_3 = QLabel(self.infoGroupBox)
        self.label_3.setObjectName(u"label_3")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy1)

        self.gridLayout_9.addWidget(self.label_3, 0, 0, 1, 1)

        self.label_20 = QLabel(self.infoGroupBox)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_9.addWidget(self.label_20, 6, 0, 1, 1)

        self.fmiVersionLabel = QLabel(self.infoGroupBox)
        self.fmiVersionLabel.setObjectName(u"fmiVersionLabel")
        sizePolicy.setHeightForWidth(self.fmiVersionLabel.sizePolicy().hasHeightForWidth())
        self.fmiVersionLabel.setSizePolicy(sizePolicy)
        self.fmiVersionLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_9.addWidget(self.fmiVersionLabel, 0, 1, 1, 1)

        self.numberOfVariablesLabel = QLabel(self.infoGroupBox)
        self.numberOfVariablesLabel.setObjectName(u"numberOfVariablesLabel")

        self.gridLayout_9.addWidget(self.numberOfVariablesLabel, 6, 1, 1, 1)

        self.fmiTypeLabel = QLabel(self.infoGroupBox)
        self.fmiTypeLabel.setObjectName(u"fmiTypeLabel")

        self.gridLayout_9.addWidget(self.fmiTypeLabel, 1, 1, 1, 1)

        self.label_8 = QLabel(self.infoGroupBox)
        self.label_8.setObjectName(u"label_8")
        sizePolicy1.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy1)

        self.gridLayout_9.addWidget(self.label_8, 7, 0, 1, 1)

        self.numberOfEventIndicatorsLabel = QLabel(self.infoGroupBox)
        self.numberOfEventIndicatorsLabel.setObjectName(u"numberOfEventIndicatorsLabel")
        sizePolicy.setHeightForWidth(self.numberOfEventIndicatorsLabel.sizePolicy().hasHeightForWidth())
        self.numberOfEventIndicatorsLabel.setSizePolicy(sizePolicy)
        self.numberOfEventIndicatorsLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_9.addWidget(self.numberOfEventIndicatorsLabel, 5, 1, 1, 1)

        self.label_12 = QLabel(self.infoGroupBox)
        self.label_12.setObjectName(u"label_12")
        sizePolicy1.setHeightForWidth(self.label_12.sizePolicy().hasHeightForWidth())
        self.label_12.setSizePolicy(sizePolicy1)

        self.gridLayout_9.addWidget(self.label_12, 5, 0, 1, 1)

        self.label_10 = QLabel(self.infoGroupBox)
        self.label_10.setObjectName(u"label_10")
        sizePolicy1.setHeightForWidth(self.label_10.sizePolicy().hasHeightForWidth())
        self.label_10.setSizePolicy(sizePolicy1)

        self.gridLayout_9.addWidget(self.label_10, 4, 0, 1, 1)

        self.label_4 = QLabel(self.infoGroupBox)
        self.label_4.setObjectName(u"label_4")
        sizePolicy1.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy1)
        self.label_4.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.gridLayout_9.addWidget(self.label_4, 2, 0, 1, 1)

        self.platformsLabel = QLabel(self.infoGroupBox)
        self.platformsLabel.setObjectName(u"platformsLabel")

        self.gridLayout_9.addWidget(self.platformsLabel, 3, 1, 1, 1)

        self.generationDateAndTimeLabel = QLabel(self.infoGroupBox)
        self.generationDateAndTimeLabel.setObjectName(u"generationDateAndTimeLabel")
        sizePolicy.setHeightForWidth(self.generationDateAndTimeLabel.sizePolicy().hasHeightForWidth())
        self.generationDateAndTimeLabel.setSizePolicy(sizePolicy)
        self.generationDateAndTimeLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_9.addWidget(self.generationDateAndTimeLabel, 7, 1, 1, 1)

        self.label_5 = QLabel(self.infoGroupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_9.addWidget(self.label_5, 1, 0, 1, 1)

        self.label = QLabel(self.infoGroupBox)
        self.label.setObjectName(u"label")

        self.gridLayout_9.addWidget(self.label, 3, 0, 1, 1)

        self.numberOfContinuousStatesLabel = QLabel(self.infoGroupBox)
        self.numberOfContinuousStatesLabel.setObjectName(u"numberOfContinuousStatesLabel")
        sizePolicy.setHeightForWidth(self.numberOfContinuousStatesLabel.sizePolicy().hasHeightForWidth())
        self.numberOfContinuousStatesLabel.setSizePolicy(sizePolicy)
        self.numberOfContinuousStatesLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_9.addWidget(self.numberOfContinuousStatesLabel, 4, 1, 1, 1)

        self.descriptionLabel = QLabel(self.infoGroupBox)
        self.descriptionLabel.setObjectName(u"descriptionLabel")
        sizePolicy.setHeightForWidth(self.descriptionLabel.sizePolicy().hasHeightForWidth())
        self.descriptionLabel.setSizePolicy(sizePolicy)
        self.descriptionLabel.setWordWrap(True)
        self.descriptionLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_9.addWidget(self.descriptionLabel, 9, 1, 1, 2)

        self.label_22 = QLabel(self.infoGroupBox)
        self.label_22.setObjectName(u"label_22")
        sizePolicy1.setHeightForWidth(self.label_22.sizePolicy().hasHeightForWidth())
        self.label_22.setSizePolicy(sizePolicy1)
        self.label_22.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.gridLayout_9.addWidget(self.label_22, 9, 0, 1, 1)

        self.generationToolLabel = QLabel(self.infoGroupBox)
        self.generationToolLabel.setObjectName(u"generationToolLabel")
        sizePolicy.setHeightForWidth(self.generationToolLabel.sizePolicy().hasHeightForWidth())
        self.generationToolLabel.setSizePolicy(sizePolicy)
        self.generationToolLabel.setWordWrap(True)
        self.generationToolLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.gridLayout_9.addWidget(self.generationToolLabel, 8, 1, 1, 2)

        self.label_7 = QLabel(self.infoGroupBox)
        self.label_7.setObjectName(u"label_7")
        sizePolicy1.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy1)
        self.label_7.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.gridLayout_9.addWidget(self.label_7, 8, 0, 1, 1)

        self.modelImageLabel = QLabel(self.infoGroupBox)
        self.modelImageLabel.setObjectName(u"modelImageLabel")
        self.modelImageLabel.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout_9.addWidget(self.modelImageLabel, 0, 2, 8, 1)


        self.verticalLayout.addWidget(self.infoGroupBox)

        self.settingsGroupBox = QGroupBox(self.settingsPage)
        self.settingsGroupBox.setObjectName(u"settingsGroupBox")
        self.settingsGroupBox.setFlat(True)
        self.gridLayout_13 = QGridLayout(self.settingsGroupBox)
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.label_14 = QLabel(self.settingsGroupBox)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_13.addWidget(self.label_14, 2, 0, 1, 1)

        self.applyDefaultStartValuesCheckBox = QCheckBox(self.settingsGroupBox)
        self.applyDefaultStartValuesCheckBox.setObjectName(u"applyDefaultStartValuesCheckBox")

        self.gridLayout_13.addWidget(self.applyDefaultStartValuesCheckBox, 6, 0, 1, 2)

        self.inputCheckBox = QCheckBox(self.settingsGroupBox)
        self.inputCheckBox.setObjectName(u"inputCheckBox")

        self.gridLayout_13.addWidget(self.inputCheckBox, 5, 0, 1, 1)

        self.label_2 = QLabel(self.settingsGroupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout_13.addWidget(self.label_2, 1, 0, 1, 1)

        self.selectInputButton = QToolButton(self.settingsGroupBox)
        self.selectInputButton.setObjectName(u"selectInputButton")
        self.selectInputButton.setEnabled(False)
        self.selectInputButton.setMinimumSize(QSize(45, 22))
        self.selectInputButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)

        self.gridLayout_13.addWidget(self.selectInputButton, 5, 2, 1, 1)

        self.logFMICallsCheckBox = QCheckBox(self.settingsGroupBox)
        self.logFMICallsCheckBox.setObjectName(u"logFMICallsCheckBox")

        self.gridLayout_13.addWidget(self.logFMICallsCheckBox, 7, 0, 1, 2)

        self.debugLoggingCheckBox = QCheckBox(self.settingsGroupBox)
        self.debugLoggingCheckBox.setObjectName(u"debugLoggingCheckBox")

        self.gridLayout_13.addWidget(self.debugLoggingCheckBox, 8, 0, 1, 2)

        self.label_13 = QLabel(self.settingsGroupBox)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_13.addWidget(self.label_13, 0, 0, 1, 1)

        self.inputFilenameLineEdit = QLineEdit(self.settingsGroupBox)
        self.inputFilenameLineEdit.setObjectName(u"inputFilenameLineEdit")
        self.inputFilenameLineEdit.setEnabled(False)

        self.gridLayout_13.addWidget(self.inputFilenameLineEdit, 5, 1, 1, 1)

        self.widget_3 = QWidget(self.settingsGroupBox)
        self.widget_3.setObjectName(u"widget_3")
        self.horizontalLayout_2 = QHBoxLayout(self.widget_3)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.stepSizeLineEdit = QLineEdit(self.widget_3)
        self.stepSizeLineEdit.setObjectName(u"stepSizeLineEdit")
        self.stepSizeLineEdit.setMinimumSize(QSize(70, 0))
        self.stepSizeLineEdit.setMaximumSize(QSize(70, 16777215))

        self.horizontalLayout_2.addWidget(self.stepSizeLineEdit)

        self.horizontalSpacer_4 = QSpacerItem(336, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.gridLayout_13.addWidget(self.widget_3, 1, 1, 1, 1)

        self.widget_10 = QWidget(self.settingsGroupBox)
        self.widget_10.setObjectName(u"widget_10")
        self.horizontalLayout_9 = QHBoxLayout(self.widget_10)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.solverComboBox = QComboBox(self.widget_10)
        self.solverComboBox.addItem("")
        self.solverComboBox.addItem("")
        self.solverComboBox.setObjectName(u"solverComboBox")
        self.solverComboBox.setMinimumSize(QSize(100, 0))
        self.solverComboBox.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToContents)

        self.horizontalLayout_9.addWidget(self.solverComboBox)

        self.horizontalSpacer_11 = QSpacerItem(340, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_11)


        self.gridLayout_13.addWidget(self.widget_10, 0, 1, 1, 1)

        self.widget_11 = QWidget(self.settingsGroupBox)
        self.widget_11.setObjectName(u"widget_11")
        self.horizontalLayout_10 = QHBoxLayout(self.widget_11)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, 0, 0, 0)
        self.relativeToleranceLineEdit = QLineEdit(self.widget_11)
        self.relativeToleranceLineEdit.setObjectName(u"relativeToleranceLineEdit")
        self.relativeToleranceLineEdit.setMinimumSize(QSize(70, 0))
        self.relativeToleranceLineEdit.setMaximumSize(QSize(70, 16777215))

        self.horizontalLayout_10.addWidget(self.relativeToleranceLineEdit)

        self.horizontalSpacer_12 = QSpacerItem(359, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_10.addItem(self.horizontalSpacer_12)


        self.gridLayout_13.addWidget(self.widget_11, 2, 1, 1, 1)

        self.widget_5 = QWidget(self.settingsGroupBox)
        self.widget_5.setObjectName(u"widget_5")
        self.horizontalLayout_4 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.widget_7 = QWidget(self.widget_5)
        self.widget_7.setObjectName(u"widget_7")
        self.horizontalLayout_6 = QHBoxLayout(self.widget_7)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.maxSamplesLineEdit = QLineEdit(self.widget_7)
        self.maxSamplesLineEdit.setObjectName(u"maxSamplesLineEdit")
        self.maxSamplesLineEdit.setMinimumSize(QSize(70, 0))
        self.maxSamplesLineEdit.setMaximumSize(QSize(70, 16777215))

        self.horizontalLayout_6.addWidget(self.maxSamplesLineEdit)

        self.horizontalSpacer_6 = QSpacerItem(334, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_6)


        self.horizontalLayout_4.addWidget(self.widget_7)


        self.gridLayout_13.addWidget(self.widget_5, 4, 1, 1, 1)

        self.outputIntervalRadioButton = QRadioButton(self.settingsGroupBox)
        self.outputIntervalRadioButton.setObjectName(u"outputIntervalRadioButton")
        self.outputIntervalRadioButton.setChecked(False)

        self.gridLayout_13.addWidget(self.outputIntervalRadioButton, 3, 0, 1, 1)

        self.widget_2 = QWidget(self.settingsGroupBox)
        self.widget_2.setObjectName(u"widget_2")
        self.horizontalLayout_3 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.outputIntervalLineEdit = QLineEdit(self.widget_2)
        self.outputIntervalLineEdit.setObjectName(u"outputIntervalLineEdit")
        self.outputIntervalLineEdit.setEnabled(False)
        self.outputIntervalLineEdit.setMinimumSize(QSize(70, 0))
        self.outputIntervalLineEdit.setMaximumSize(QSize(70, 16777215))

        self.horizontalLayout_3.addWidget(self.outputIntervalLineEdit)

        self.horizontalSpacer_3 = QSpacerItem(558, 18, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_3)


        self.gridLayout_13.addWidget(self.widget_2, 3, 1, 1, 1)

        self.maxSamplesRadioButton = QRadioButton(self.settingsGroupBox)
        self.maxSamplesRadioButton.setObjectName(u"maxSamplesRadioButton")
        self.maxSamplesRadioButton.setChecked(True)

        self.gridLayout_13.addWidget(self.maxSamplesRadioButton, 4, 0, 1, 1)


        self.verticalLayout.addWidget(self.settingsGroupBox)

        self.portsGroupBox = QGroupBox(self.settingsPage)
        self.portsGroupBox.setObjectName(u"portsGroupBox")
        self.portsGroupBox.setFlat(True)
        self.verticalLayout_4 = QVBoxLayout(self.portsGroupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 5, 0, 0)
        self.graphicsView = QGraphicsView(self.portsGroupBox)
        self.graphicsView.setObjectName(u"graphicsView")
        self.graphicsView.setFrameShape(QFrame.Shape.NoFrame)

        self.verticalLayout_4.addWidget(self.graphicsView)


        self.verticalLayout.addWidget(self.portsGroupBox)

        self.stackedWidget.addWidget(self.settingsPage)
        self.documentationPage = QWidget()
        self.documentationPage.setObjectName(u"documentationPage")
        self.gridLayout_2 = QGridLayout(self.documentationPage)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.webEngineView = QWebEngineView(self.documentationPage)
        self.webEngineView.setObjectName(u"webEngineView")

        self.gridLayout_2.addWidget(self.webEngineView, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.documentationPage)
        self.filesPage = QWidget()
        self.filesPage.setObjectName(u"filesPage")
        self.gridLayout_4 = QGridLayout(self.filesPage)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.filesTreeView = QTreeView(self.filesPage)
        self.filesTreeView.setObjectName(u"filesTreeView")
        self.filesTreeView.setFrameShape(QFrame.Shape.NoFrame)

        self.gridLayout_4.addWidget(self.filesTreeView, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.filesPage)
        self.logPage = QWidget()
        self.logPage.setObjectName(u"logPage")
        self.verticalLayout_3 = QVBoxLayout(self.logPage)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.logWidget = QWidget(self.logPage)
        self.logWidget.setObjectName(u"logWidget")
        self.logWidget.setStyleSheet(u"QToolButton {\n"
"     padding: 1px;\n"
"	 border: 1px solid transparent;\n"
"	 border-radius: 2px;\n"
"     background: transparent;\n"
"	height: 14px;\n"
"}\n"
"\n"
"QToolButton:hover {\n"
"		border: 1px solid  rgba( 92, 163, 255, 20% );\n"
"		background-color: rgba( 92, 163, 255, 10% );\n"
"}\n"
"\n"
"QToolButton:checked, QToolButton:hover:pressed {\n"
"		border: 1px solid  rgba( 92, 163, 255, 50% );\n"
"		background-color: rgba( 92, 163, 255, 25% );\n"
"}")
        self.horizontalLayout_11 = QHBoxLayout(self.logWidget)
        self.horizontalLayout_11.setSpacing(4)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, 4, 4, 6)
        self.clearLogButton = QToolButton(self.logWidget)
        self.clearLogButton.setObjectName(u"clearLogButton")
        self.clearLogButton.setMinimumSize(QSize(0, 21))
        self.clearLogButton.setAutoRaise(True)

        self.horizontalLayout_11.addWidget(self.clearLogButton)

        self.clearLogOnStartButton = QToolButton(self.logWidget)
        self.clearLogOnStartButton.setObjectName(u"clearLogOnStartButton")
        self.clearLogOnStartButton.setMinimumSize(QSize(0, 21))
        self.clearLogOnStartButton.setCheckable(True)
        self.clearLogOnStartButton.setChecked(True)
        self.clearLogOnStartButton.setAutoRaise(True)

        self.horizontalLayout_11.addWidget(self.clearLogOnStartButton)

        self.logFilterLineEdit = QLineEdit(self.logWidget)
        self.logFilterLineEdit.setObjectName(u"logFilterLineEdit")
        self.logFilterLineEdit.setStyleSheet(u"QLineEdit {\n"
"     border: 1px solid #ddd;\n"
"	 border-radius: 2px;\n"
"     padding: 1px 5px 2px 5px;\n"
"     background: transparent;\n"
"	font-size: 11px;\n"
" }")
        self.logFilterLineEdit.setClearButtonEnabled(True)

        self.horizontalLayout_11.addWidget(self.logFilterLineEdit)

        self.showDebugMessagesButton = QToolButton(self.logWidget)
        self.showDebugMessagesButton.setObjectName(u"showDebugMessagesButton")
        icon13 = QIcon()
        icon13.addFile(u":/icons/light/debug.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.showDebugMessagesButton.setIcon(icon13)
        self.showDebugMessagesButton.setCheckable(True)
        self.showDebugMessagesButton.setChecked(False)
        self.showDebugMessagesButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.showDebugMessagesButton.setAutoRaise(True)

        self.horizontalLayout_11.addWidget(self.showDebugMessagesButton)

        self.showInfoMessagesButton = QToolButton(self.logWidget)
        self.showInfoMessagesButton.setObjectName(u"showInfoMessagesButton")
        icon14 = QIcon()
        icon14.addFile(u":/icons/light/info.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.showInfoMessagesButton.setIcon(icon14)
        self.showInfoMessagesButton.setCheckable(True)
        self.showInfoMessagesButton.setChecked(True)
        self.showInfoMessagesButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.showInfoMessagesButton.setAutoRaise(True)

        self.horizontalLayout_11.addWidget(self.showInfoMessagesButton)

        self.showWarningMessagesButton = QToolButton(self.logWidget)
        self.showWarningMessagesButton.setObjectName(u"showWarningMessagesButton")
        icon15 = QIcon()
        icon15.addFile(u":/icons/light/warning.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.showWarningMessagesButton.setIcon(icon15)
        self.showWarningMessagesButton.setCheckable(True)
        self.showWarningMessagesButton.setChecked(True)
        self.showWarningMessagesButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.showWarningMessagesButton.setAutoRaise(True)

        self.horizontalLayout_11.addWidget(self.showWarningMessagesButton)

        self.showErrorMessagesButton = QToolButton(self.logWidget)
        self.showErrorMessagesButton.setObjectName(u"showErrorMessagesButton")
        icon16 = QIcon()
        icon16.addFile(u":/icons/light/error.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.showErrorMessagesButton.setIcon(icon16)
        self.showErrorMessagesButton.setCheckable(True)
        self.showErrorMessagesButton.setChecked(True)
        self.showErrorMessagesButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.showErrorMessagesButton.setAutoRaise(True)

        self.horizontalLayout_11.addWidget(self.showErrorMessagesButton)


        self.verticalLayout_3.addWidget(self.logWidget)

        self.logWebEngineView = QWebEngineView(self.logPage)
        self.logWebEngineView.setObjectName(u"logWebEngineView")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.logWebEngineView.sizePolicy().hasHeightForWidth())
        self.logWebEngineView.setSizePolicy(sizePolicy2)
        self.logWebEngineView.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self.verticalLayout_3.addWidget(self.logWebEngineView)

        self.stackedWidget.addWidget(self.logPage)
        self.resultPage = QWidget()
        self.resultPage.setObjectName(u"resultPage")
        self.gridLayout_3 = QGridLayout(self.resultPage)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.resultStackedWidget = QStackedWidget(self.resultPage)
        self.resultStackedWidget.setObjectName(u"resultStackedWidget")
        self.noResultPage = QWidget()
        self.noResultPage.setObjectName(u"noResultPage")
        self.gridLayout_7 = QGridLayout(self.noResultPage)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label_6 = QLabel(self.noResultPage)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_7.addWidget(self.label_6, 0, 0, 1, 1)

        self.resultStackedWidget.addWidget(self.noResultPage)
        self.resultViewPage = QWidget()
        self.resultViewPage.setObjectName(u"resultViewPage")
        self.gridLayout_8 = QGridLayout(self.resultViewPage)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(0, 0, 0, 0)
        self.resultWebEngineView = QWebEngineView(self.resultViewPage)
        self.resultWebEngineView.setObjectName(u"resultWebEngineView")
        self.resultWebEngineView.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.resultWebEngineView.setUrl(QUrl(u"about:blank"))

        self.gridLayout_8.addWidget(self.resultWebEngineView, 0, 0, 1, 1)

        self.resultStackedWidget.addWidget(self.resultViewPage)

        self.gridLayout_3.addWidget(self.resultStackedWidget, 0, 0, 1, 1)

        self.stackedWidget.addWidget(self.resultPage)

        self.horizontalLayout_12.addWidget(self.stackedWidget)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1125, 33))
        self.menu_File = QMenu(self.menubar)
        self.menu_File.setObjectName(u"menu_File")
        self.menu_Help = QMenu(self.menubar)
        self.menu_Help.setObjectName(u"menu_Help")
        self.menuFMI_Specifications = QMenu(self.menu_Help)
        self.menuFMI_Specifications.setObjectName(u"menuFMI_Specifications")
        self.menu_Tools = QMenu(self.menubar)
        self.menu_Tools.setObjectName(u"menu_Tools")
        self.menuAddRemoting = QMenu(self.menu_Tools)
        self.menuAddRemoting.setObjectName(u"menuAddRemoting")
        MainWindow.setMenuBar(self.menubar)
        self.statusBar = QStatusBar(MainWindow)
        self.statusBar.setObjectName(u"statusBar")
        self.statusBar.setStyleSheet(u"QStatusBar {\n"
"	border-top: 1px solid palette(midlight);\n"
"}\n"
"\n"
"QStatusBar::item {\n"
"	border: none;\n"
"}\n"
"")
        self.statusBar.setSizeGripEnabled(False)
        MainWindow.setStatusBar(self.statusBar)
        self.dockWidget = QDockWidget(MainWindow)
        self.dockWidget.setObjectName(u"dockWidget")
        self.dockWidget.setStyleSheet(u"QDockWidget > QWidget {\n"
"	border-right: 1px solid palette(midlight);\n"
"}")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.gridLayout = QGridLayout(self.dockWidgetContents)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 1, 0)
        self.filterWidget = QWidget(self.dockWidgetContents)
        self.filterWidget.setObjectName(u"filterWidget")
        self.filterWidget.setStyleSheet(u"QToolButton {\n"
"     padding: 1px;\n"
"	 border: 1px solid transparent;\n"
"	 border-radius: 2px;\n"
"     background: transparent;\n"
"	height: 14px;\n"
"}\n"
"\n"
"QToolButton:hover {\n"
"		border: 1px solid  rgba( 92, 163, 255, 20% );\n"
"		background-color: rgba( 92, 163, 255, 10% );\n"
"}\n"
"\n"
"QToolButton:checked, QToolButton:hover:pressed {\n"
"		border: 1px solid  rgba( 92, 163, 255, 50% );\n"
"		background-color: rgba( 92, 163, 255, 25% );\n"
"}")
        self.horizontalLayout_5 = QHBoxLayout(self.filterWidget)
        self.horizontalLayout_5.setSpacing(4)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(4, 5, 4, 0)
        self.filterLineEdit = QLineEdit(self.filterWidget)
        self.filterLineEdit.setObjectName(u"filterLineEdit")
        self.filterLineEdit.setClearButtonEnabled(True)

        self.horizontalLayout_5.addWidget(self.filterLineEdit)

        self.filterToolButton = QToolButton(self.filterWidget)
        self.filterToolButton.setObjectName(u"filterToolButton")
        self.filterToolButton.setStyleSheet(u"padding-right: 10px;")
        icon17 = QIcon()
        icon17.addFile(u":/icons/dark/filter.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.filterToolButton.setIcon(icon17)
        self.filterToolButton.setCheckable(True)
        self.filterToolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.filterToolButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)
        self.filterToolButton.setAutoRaise(True)

        self.horizontalLayout_5.addWidget(self.filterToolButton)

        self.tableViewToolButton = QToolButton(self.filterWidget)
        self.tableViewToolButton.setObjectName(u"tableViewToolButton")
        self.tableViewToolButton.setStyleSheet(u"text-align:left;")
        icon18 = QIcon()
        icon18.addFile(u":/icons/dark/list.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.tableViewToolButton.setIcon(icon18)
        self.tableViewToolButton.setCheckable(True)
        self.tableViewToolButton.setAutoRaise(True)

        self.horizontalLayout_5.addWidget(self.tableViewToolButton)


        self.gridLayout.addWidget(self.filterWidget, 0, 0, 1, 1)

        self.variablesStackedWidget = QStackedWidget(self.dockWidgetContents)
        self.variablesStackedWidget.setObjectName(u"variablesStackedWidget")
        self.treePage = QWidget()
        self.treePage.setObjectName(u"treePage")
        self.gridLayout_5 = QGridLayout(self.treePage)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.treeView = QTreeView(self.treePage)
        self.treeView.setObjectName(u"treeView")
        self.treeView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.treeView.setFrameShape(QFrame.Shape.NoFrame)
        self.treeView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)

        self.gridLayout_5.addWidget(self.treeView, 0, 0, 1, 1)

        self.variablesStackedWidget.addWidget(self.treePage)
        self.tablePage = QWidget()
        self.tablePage.setObjectName(u"tablePage")
        self.gridLayout_6 = QGridLayout(self.tablePage)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.gridLayout_6.setContentsMargins(0, 0, 0, 0)
        self.tableView = QTreeView(self.tablePage)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tableView.setFrameShape(QFrame.Shape.NoFrame)
        self.tableView.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableView.setRootIsDecorated(False)

        self.gridLayout_6.addWidget(self.tableView, 0, 0, 1, 1)

        self.variablesStackedWidget.addWidget(self.tablePage)

        self.gridLayout.addWidget(self.variablesStackedWidget, 1, 0, 1, 1)

        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dockWidget)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
        self.toolBar.setMovable(False)
        self.toolBar.setFloatable(False)
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menu_Tools.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())
        self.menu_File.addAction(self.actionShowNewFMUDialog)
        self.menu_File.addAction(self.actionNewWindow)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionOpen)
        self.menu_File.addAction(self.actionSave)
        self.menu_File.addAction(self.actionSaveAs)
        self.menu_File.addAction(self.actionReload)
        self.menu_File.addAction(self.actionOpenUnzipDirectory)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionLoadStartValues)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionSaveResult)
        self.menu_File.addAction(self.actionSavePlottedResult)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionClose)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionExit)
        self.menu_Help.addAction(self.menuFMI_Specifications.menuAction())
        self.menu_Help.addAction(self.actionOpenTestFMUs)
        self.menu_Help.addSeparator()
        self.menu_Help.addAction(self.actionOpenWebsite)
        self.menu_Help.addAction(self.actionShowReleaseNotes)
        self.menu_Help.addSeparator()
        self.menu_Help.addAction(self.actionShowAboutDialog)
        self.menuFMI_Specifications.addAction(self.actionOpenFMI3Spec)
        self.menuFMI_Specifications.addSeparator()
        self.menuFMI_Specifications.addAction(self.actionOpenFMI2Spec)
        self.menuFMI_Specifications.addSeparator()
        self.menuFMI_Specifications.addAction(self.actionOpenFMI1SpecCS)
        self.menuFMI_Specifications.addAction(self.actionOpenFMI1SpecME)
        self.menu_Tools.addAction(self.actionCreateDesktopShortcut)
        self.menu_Tools.addAction(self.actionAddFileAssociation)
        self.menu_Tools.addSeparator()
        self.menu_Tools.addAction(self.actionBuildPlatformBinary)
        self.menu_Tools.addAction(self.actionValidateFMU)
        self.menu_Tools.addAction(self.actionRemoveSourceCode)
        self.menu_Tools.addAction(self.actionCreateJupyterNotebook)
        self.menu_Tools.addAction(self.actionCreateCMakeProject)
        self.menu_Tools.addAction(self.menuAddRemoting.menuAction())
        self.menu_Tools.addAction(self.actionAddCoSimulationWrapper)
        self.menuAddRemoting.addAction(self.actionAddWindows32Remoting)
        self.menuAddRemoting.addAction(self.actionAddLinux64Remoting)
        self.toolBar.addAction(self.actionShowNewFMUDialog)
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionSave)
        self.toolBar.addAction(self.actionReload)
        self.toolBar.addAction(self.actionBuildPlatformBinary)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionShowSettings)
        self.toolBar.addAction(self.actionShowFiles)
        self.toolBar.addAction(self.actionShowDocumentation)
        self.toolBar.addAction(self.actionShowLog)
        self.toolBar.addAction(self.actionShowResults)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionSimulate)

        self.retranslateUi(MainWindow)
        self.actionClose.triggered.connect(MainWindow.close)
        self.inputCheckBox.toggled.connect(self.inputFilenameLineEdit.setEnabled)
        self.inputCheckBox.toggled.connect(self.selectInputButton.setEnabled)
        self.outputIntervalRadioButton.toggled.connect(self.outputIntervalLineEdit.setEnabled)
        self.maxSamplesRadioButton.toggled.connect(self.maxSamplesLineEdit.setEnabled)

        self.stackedWidget.setCurrentIndex(0)
        self.solverComboBox.setCurrentIndex(1)
        self.variablesStackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"FMPy", None))
        self.actionSimulate.setText(QCoreApplication.translate("MainWindow", u"Simulate", None))
#if QT_CONFIG(tooltip)
        self.actionSimulate.setToolTip(QCoreApplication.translate("MainWindow", u"Start simulation", None))
#endif // QT_CONFIG(tooltip)
        self.actionShowSettings.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
#if QT_CONFIG(tooltip)
        self.actionShowSettings.setToolTip(QCoreApplication.translate("MainWindow", u"Show settings", None))
#endif // QT_CONFIG(tooltip)
        self.actionOpen.setText(QCoreApplication.translate("MainWindow", u"&Open", None))
#if QT_CONFIG(tooltip)
        self.actionOpen.setToolTip(QCoreApplication.translate("MainWindow", u"Open file", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionOpen.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+O", None))
#endif // QT_CONFIG(shortcut)
        self.actionShowResults.setText(QCoreApplication.translate("MainWindow", u"Results", None))
#if QT_CONFIG(tooltip)
        self.actionShowResults.setToolTip(QCoreApplication.translate("MainWindow", u"Show results", None))
#endif // QT_CONFIG(tooltip)
        self.actionNewWindow.setText(QCoreApplication.translate("MainWindow", u"&New Window", None))
#if QT_CONFIG(shortcut)
        self.actionNewWindow.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionFilterInputs.setText(QCoreApplication.translate("MainWindow", u"Inputs", None))
#if QT_CONFIG(tooltip)
        self.actionFilterInputs.setToolTip(QCoreApplication.translate("MainWindow", u"Filter input variables", None))
#endif // QT_CONFIG(tooltip)
        self.actionFilterOutputs.setText(QCoreApplication.translate("MainWindow", u"Outputs", None))
#if QT_CONFIG(tooltip)
        self.actionFilterOutputs.setToolTip(QCoreApplication.translate("MainWindow", u"Filter output variables", None))
#endif // QT_CONFIG(tooltip)
        self.actionFilterParameters.setText(QCoreApplication.translate("MainWindow", u"Parameters", None))
#if QT_CONFIG(tooltip)
        self.actionFilterParameters.setToolTip(QCoreApplication.translate("MainWindow", u"Filter parameters", None))
#endif // QT_CONFIG(tooltip)
        self.actionFilterLocalVariables.setText(QCoreApplication.translate("MainWindow", u"Local", None))
#if QT_CONFIG(tooltip)
        self.actionFilterLocalVariables.setToolTip(QCoreApplication.translate("MainWindow", u"Filter local variables", None))
#endif // QT_CONFIG(tooltip)
        self.actionFilterIndependentVariables.setText(QCoreApplication.translate("MainWindow", u"Independent", None))
#if QT_CONFIG(tooltip)
        self.actionFilterIndependentVariables.setToolTip(QCoreApplication.translate("MainWindow", u"Filter independent variables", None))
#endif // QT_CONFIG(tooltip)
        self.actionFilterCalculatedParameters.setText(QCoreApplication.translate("MainWindow", u"Calculated Parameters", None))
#if QT_CONFIG(tooltip)
        self.actionFilterCalculatedParameters.setToolTip(QCoreApplication.translate("MainWindow", u"Filter calculated parameters", None))
#endif // QT_CONFIG(tooltip)
        self.actionOpenFMI2Spec.setText(QCoreApplication.translate("MainWindow", u"FMI 2.0.5", None))
#if QT_CONFIG(tooltip)
        self.actionOpenFMI2Spec.setToolTip(QCoreApplication.translate("MainWindow", u"Open FMI Specification 2.0.5", None))
#endif // QT_CONFIG(tooltip)
        self.actionOpenFMI1SpecCS.setText(QCoreApplication.translate("MainWindow", u"FMI 1.0.1 for Co-Simulation", None))
#if QT_CONFIG(tooltip)
        self.actionOpenFMI1SpecCS.setToolTip(QCoreApplication.translate("MainWindow", u"Open FMI 1.0.1 Specification for Co-Simulation", None))
#endif // QT_CONFIG(tooltip)
        self.actionOpenFMI1SpecME.setText(QCoreApplication.translate("MainWindow", u"FMI 1.0.1 for Model Exchange", None))
#if QT_CONFIG(tooltip)
        self.actionOpenFMI1SpecME.setToolTip(QCoreApplication.translate("MainWindow", u"Open FMI Specification 1.0.1 for Model Exchange", None))
#endif // QT_CONFIG(tooltip)
        self.actionClose.setText(QCoreApplication.translate("MainWindow", u"&Close", None))
#if QT_CONFIG(tooltip)
        self.actionClose.setToolTip(QCoreApplication.translate("MainWindow", u"Close the current window", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionClose.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+W", None))
#endif // QT_CONFIG(shortcut)
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"E&xit", None))
#if QT_CONFIG(tooltip)
        self.actionExit.setToolTip(QCoreApplication.translate("MainWindow", u"Close all windows", None))
#endif // QT_CONFIG(tooltip)
        self.actionShowLog.setText(QCoreApplication.translate("MainWindow", u"Log", None))
#if QT_CONFIG(tooltip)
        self.actionShowLog.setToolTip(QCoreApplication.translate("MainWindow", u"Show log", None))
#endif // QT_CONFIG(tooltip)
        self.actionOpenTestFMUs.setText(QCoreApplication.translate("MainWindow", u"&Test FMUs", None))
#if QT_CONFIG(tooltip)
        self.actionOpenTestFMUs.setToolTip(QCoreApplication.translate("MainWindow", u"Test FMUs on fmi-standard.org", None))
#endif // QT_CONFIG(tooltip)
        self.actionSaveResult.setText(QCoreApplication.translate("MainWindow", u"&Save Result...", None))
#if QT_CONFIG(shortcut)
        self.actionSaveResult.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionSavePlottedResult.setText(QCoreApplication.translate("MainWindow", u"Save &Plotted Result...", None))
#if QT_CONFIG(tooltip)
        self.actionSavePlottedResult.setToolTip(QCoreApplication.translate("MainWindow", u"Save plotted result", None))
#endif // QT_CONFIG(tooltip)
        self.actionCreateDesktopShortcut.setText(QCoreApplication.translate("MainWindow", u"Create Desktop &Shortcut", None))
        self.actionShowAboutDialog.setText(QCoreApplication.translate("MainWindow", u"&About FMPy", None))
        self.actionOpenWebsite.setText(QCoreApplication.translate("MainWindow", u"FMPy &Website", None))
        self.actionAddFileAssociation.setText(QCoreApplication.translate("MainWindow", u"&Associate with *.fmu Files", None))
#if QT_CONFIG(tooltip)
        self.actionAddFileAssociation.setToolTip(QCoreApplication.translate("MainWindow", u"Add file association for *.fmu", None))
#endif // QT_CONFIG(tooltip)
        self.actionShowReleaseNotes.setText(QCoreApplication.translate("MainWindow", u"&Release Notes", None))
        self.actionReload.setText(QCoreApplication.translate("MainWindow", u"&Reload", None))
#if QT_CONFIG(shortcut)
        self.actionReload.setShortcut(QCoreApplication.translate("MainWindow", u"F5", None))
#endif // QT_CONFIG(shortcut)
        self.actionSaveChanges.setText(QCoreApplication.translate("MainWindow", u"Save Changes", None))
        self.actionLoadStartValues.setText(QCoreApplication.translate("MainWindow", u"Load Start Values", None))
        self.actionCreateCMakeProject.setText(QCoreApplication.translate("MainWindow", u"Create C&Make Project...", None))
        self.actionAddCoSimulationWrapper.setText(QCoreApplication.translate("MainWindow", u"Add Co-Simulation &Wrapper", None))
        self.actionCreateJupyterNotebook.setText(QCoreApplication.translate("MainWindow", u"Create &Jupyter Notebook...", None))
        self.actionValidateFMU.setText(QCoreApplication.translate("MainWindow", u"&Validate FMU", None))
        self.actionAddLinux64Remoting.setText(QCoreApplication.translate("MainWindow", u"Windows 64-bit on &Linux 64-bit", None))
        self.actionAddWindows32Remoting.setText(QCoreApplication.translate("MainWindow", u"Windows 32-bit on &Windows 64-bit", None))
        self.actionShowDocumentation.setText(QCoreApplication.translate("MainWindow", u"Show documentation", None))
        self.actionShowFiles.setText(QCoreApplication.translate("MainWindow", u"Show archive contents", None))
        self.actionOpenUnzipDirectory.setText(QCoreApplication.translate("MainWindow", u"Open &Unzip Directory", None))
#if QT_CONFIG(tooltip)
        self.actionOpenUnzipDirectory.setToolTip(QCoreApplication.translate("MainWindow", u"Open unzip directory", None))
#endif // QT_CONFIG(tooltip)
        self.actionRemoveSourceCode.setText(QCoreApplication.translate("MainWindow", u"&Remove Source Code", None))
        self.actionOpenFMI3Spec.setText(QCoreApplication.translate("MainWindow", u"FMI 3.0.2", None))
#if QT_CONFIG(tooltip)
        self.actionOpenFMI3Spec.setToolTip(QCoreApplication.translate("MainWindow", u"Open FMI Specification 3.0.2", None))
#endif // QT_CONFIG(tooltip)
        self.actionShowNewFMUDialog.setText(QCoreApplication.translate("MainWindow", u"&New FMU...", None))
#if QT_CONFIG(tooltip)
        self.actionShowNewFMUDialog.setToolTip(QCoreApplication.translate("MainWindow", u"Create new FMU", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionShowNewFMUDialog.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+N", None))
#endif // QT_CONFIG(shortcut)
        self.actionBuildPlatformBinary.setText(QCoreApplication.translate("MainWindow", u"&Build Platform Binary...", None))
#if QT_CONFIG(tooltip)
        self.actionBuildPlatformBinary.setToolTip(QCoreApplication.translate("MainWindow", u"Build Platform Binary", None))
#endif // QT_CONFIG(tooltip)
        self.actionSave.setText(QCoreApplication.translate("MainWindow", u"&Save", None))
#if QT_CONFIG(tooltip)
        self.actionSave.setToolTip(QCoreApplication.translate("MainWindow", u"Save FMU", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionSave.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+S", None))
#endif // QT_CONFIG(shortcut)
        self.actionSaveAs.setText(QCoreApplication.translate("MainWindow", u"Save &As...", None))
#if QT_CONFIG(tooltip)
        self.actionSaveAs.setToolTip(QCoreApplication.translate("MainWindow", u"Save FMU as...", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(shortcut)
        self.actionSaveAs.setShortcut(QCoreApplication.translate("MainWindow", u"Ctrl+Shift+S", None))
#endif // QT_CONFIG(shortcut)
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Drop FMUs here or", None))
        self.openButton.setText(QCoreApplication.translate("MainWindow", u"open an FMU", None))
        self.recentFilesGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Recent Files", None))
        self.infoGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Model Info", None))
        self.modelNameLabel.setText("")
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"FMI Version", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"Variables", None))
        self.fmiVersionLabel.setText("")
        self.numberOfVariablesLabel.setText("")
        self.fmiTypeLabel.setText("")
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Generation Date", None))
        self.numberOfEventIndicatorsLabel.setText("")
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Event Indicators", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Continuous States", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Model Name", None))
        self.platformsLabel.setText("")
        self.generationDateAndTimeLabel.setText("")
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"FMI Type", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Platforms", None))
        self.numberOfContinuousStatesLabel.setText("")
        self.descriptionLabel.setText("")
        self.label_22.setText(QCoreApplication.translate("MainWindow", u"Description", None))
        self.generationToolLabel.setText("")
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Generation Tool", None))
        self.settingsGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Simulation", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Relative Tolerance", None))
        self.applyDefaultStartValuesCheckBox.setText(QCoreApplication.translate("MainWindow", u"Apply default start values", None))
        self.inputCheckBox.setText(QCoreApplication.translate("MainWindow", u"Input", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Step Size", None))
#if QT_CONFIG(tooltip)
        self.selectInputButton.setToolTip(QCoreApplication.translate("MainWindow", u"Select input file", None))
#endif // QT_CONFIG(tooltip)
        self.selectInputButton.setText(QCoreApplication.translate("MainWindow", u"...", None))
        self.logFMICallsCheckBox.setText(QCoreApplication.translate("MainWindow", u"Log FMI calls", None))
        self.debugLoggingCheckBox.setText(QCoreApplication.translate("MainWindow", u"Debug Logging", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Solver", None))
        self.inputFilenameLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"No input file selected", None))
        self.stepSizeLineEdit.setText(QCoreApplication.translate("MainWindow", u"1e-3", None))
        self.solverComboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"Fixed-step", None))
        self.solverComboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"Variable-step", None))

        self.relativeToleranceLineEdit.setText(QCoreApplication.translate("MainWindow", u"1e-5", None))
        self.maxSamplesLineEdit.setText(QCoreApplication.translate("MainWindow", u"500", None))
        self.outputIntervalRadioButton.setText(QCoreApplication.translate("MainWindow", u"Output Interval", None))
        self.outputIntervalLineEdit.setText(QCoreApplication.translate("MainWindow", u"1e-2", None))
        self.maxSamplesRadioButton.setText(QCoreApplication.translate("MainWindow", u"Max. Samples", None))
        self.portsGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Ports", None))
#if QT_CONFIG(tooltip)
        self.clearLogButton.setToolTip(QCoreApplication.translate("MainWindow", u"Clear messages", None))
#endif // QT_CONFIG(tooltip)
        self.clearLogButton.setText(QCoreApplication.translate("MainWindow", u"clear", None))
#if QT_CONFIG(tooltip)
        self.clearLogOnStartButton.setToolTip(QCoreApplication.translate("MainWindow", u"Clear messages on simulation start", None))
#endif // QT_CONFIG(tooltip)
        self.clearLogOnStartButton.setText(QCoreApplication.translate("MainWindow", u"clear on start", None))
        self.logFilterLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"filter messages", None))
#if QT_CONFIG(tooltip)
        self.showDebugMessagesButton.setToolTip(QCoreApplication.translate("MainWindow", u"Show debug messages", None))
#endif // QT_CONFIG(tooltip)
        self.showDebugMessagesButton.setText(QCoreApplication.translate("MainWindow", u"0", None))
#if QT_CONFIG(tooltip)
        self.showInfoMessagesButton.setToolTip(QCoreApplication.translate("MainWindow", u"Show info messages", None))
#endif // QT_CONFIG(tooltip)
        self.showInfoMessagesButton.setText(QCoreApplication.translate("MainWindow", u"0", None))
#if QT_CONFIG(tooltip)
        self.showWarningMessagesButton.setToolTip(QCoreApplication.translate("MainWindow", u"Show warning messages", None))
#endif // QT_CONFIG(tooltip)
        self.showWarningMessagesButton.setText(QCoreApplication.translate("MainWindow", u"0", None))
#if QT_CONFIG(tooltip)
        self.showErrorMessagesButton.setToolTip(QCoreApplication.translate("MainWindow", u"Show error messages", None))
#endif // QT_CONFIG(tooltip)
        self.showErrorMessagesButton.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"No variables selcted", None))
        self.menu_File.setTitle(QCoreApplication.translate("MainWindow", u"&File", None))
        self.menu_Help.setTitle(QCoreApplication.translate("MainWindow", u"&Help", None))
        self.menuFMI_Specifications.setTitle(QCoreApplication.translate("MainWindow", u"FMI &Specifications", None))
        self.menu_Tools.setTitle(QCoreApplication.translate("MainWindow", u"&Tools", None))
        self.menuAddRemoting.setTitle(QCoreApplication.translate("MainWindow", u"Add &Remoting", None))
        self.filterLineEdit.setPlaceholderText(QCoreApplication.translate("MainWindow", u"filter variables", None))
#if QT_CONFIG(tooltip)
        self.filterToolButton.setToolTip(QCoreApplication.translate("MainWindow", u"Filter variables", None))
#endif // QT_CONFIG(tooltip)
        self.filterToolButton.setText(QCoreApplication.translate("MainWindow", u"...", None))
#if QT_CONFIG(tooltip)
        self.tableViewToolButton.setToolTip(QCoreApplication.translate("MainWindow", u"Toggle list view", None))
#endif // QT_CONFIG(tooltip)
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

