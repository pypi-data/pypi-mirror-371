# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'sceneeditorwidget.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QFrame,
    QHBoxLayout, QLabel, QPushButton, QSizePolicy,
    QSplitter, QVBoxLayout, QWidget)

from cmlibs.widgets.draggablelistwidget import DraggableListWidget
from cmlibs.widgets.graphicseditorwidget import GraphicsEditorWidget
from cmlibs.widgets.regionchooserwidget import RegionChooserWidget

class Ui_SceneEditorWidget(object):
    def setupUi(self, SceneEditorWidget):
        if not SceneEditorWidget.objectName():
            SceneEditorWidget.setObjectName(u"SceneEditorWidget")
        SceneEditorWidget.resize(300, 725)
        sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SceneEditorWidget.sizePolicy().hasHeightForWidth())
        SceneEditorWidget.setSizePolicy(sizePolicy)
        self.verticalLayout = QVBoxLayout(SceneEditorWidget)
        self.verticalLayout.setSpacing(2)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(2, 2, 2, 2)
        self.splitter = QSplitter(SceneEditorWidget)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setChildrenCollapsible(False)
        self.splitterAreaWidgetContents = QWidget(self.splitter)
        self.splitterAreaWidgetContents.setObjectName(u"splitterAreaWidgetContents")
        self.verticalLayout_2 = QVBoxLayout(self.splitterAreaWidgetContents)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.region_frame = QFrame(self.splitterAreaWidgetContents)
        self.region_frame.setObjectName(u"region_frame")
        self.region_frame.setFrameShape(QFrame.StyledPanel)
        self.region_frame.setFrameShadow(QFrame.Raised)
        self.formLayout = QFormLayout(self.region_frame)
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setProperty("Margin", 2)
        self.region_label = QLabel(self.region_frame)
        self.region_label.setObjectName(u"region_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.region_label)

        self.region_chooser = RegionChooserWidget(self.region_frame)
        self.region_chooser.setObjectName(u"region_chooser")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.region_chooser)


        self.verticalLayout_2.addWidget(self.region_frame)

        self.graphics_listWidget = DraggableListWidget(self.splitterAreaWidgetContents)
        self.graphics_listWidget.setObjectName(u"graphics_listWidget")

        self.verticalLayout_2.addWidget(self.graphics_listWidget)

        self.frame = QFrame(self.splitterAreaWidgetContents)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 2, 0, 2)
        self.add_graphics_combobox = QComboBox(self.frame)
        self.add_graphics_combobox.addItem("")
        self.add_graphics_combobox.addItem("")
        self.add_graphics_combobox.addItem("")
        self.add_graphics_combobox.addItem("")
        self.add_graphics_combobox.addItem("")
        self.add_graphics_combobox.addItem("")
        self.add_graphics_combobox.addItem("")
        self.add_graphics_combobox.addItem("")
        self.add_graphics_combobox.addItem("")
        self.add_graphics_combobox.addItem("")
        self.add_graphics_combobox.setObjectName(u"add_graphics_combobox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.add_graphics_combobox.sizePolicy().hasHeightForWidth())
        self.add_graphics_combobox.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.add_graphics_combobox)

        self.delete_graphics_button = QPushButton(self.frame)
        self.delete_graphics_button.setObjectName(u"delete_graphics_button")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.delete_graphics_button.sizePolicy().hasHeightForWidth())
        self.delete_graphics_button.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.delete_graphics_button)


        self.verticalLayout_2.addWidget(self.frame)

        self.splitter.addWidget(self.splitterAreaWidgetContents)
        self.graphics_editor = GraphicsEditorWidget(self.splitter)
        self.graphics_editor.setObjectName(u"graphics_editor")
        sizePolicy3 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.graphics_editor.sizePolicy().hasHeightForWidth())
        self.graphics_editor.setSizePolicy(sizePolicy3)
        self.splitter.addWidget(self.graphics_editor)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(SceneEditorWidget)
        self.graphics_listWidget.itemClicked.connect(SceneEditorWidget.graphicsListItemClicked)
        self.add_graphics_combobox.currentTextChanged.connect(SceneEditorWidget.addGraphicsEntered)
        self.delete_graphics_button.clicked.connect(SceneEditorWidget.deleteGraphicsClicked)

        QMetaObject.connectSlotsByName(SceneEditorWidget)
    # setupUi

    def retranslateUi(self, SceneEditorWidget):
        SceneEditorWidget.setWindowTitle(QCoreApplication.translate("SceneEditorWidget", u"Scene Editor", None))
        self.region_label.setText(QCoreApplication.translate("SceneEditorWidget", u"Region:", None))
        self.add_graphics_combobox.setItemText(0, QCoreApplication.translate("SceneEditorWidget", u"Add...", None))
        self.add_graphics_combobox.setItemText(1, QCoreApplication.translate("SceneEditorWidget", u"---", None))
        self.add_graphics_combobox.setItemText(2, QCoreApplication.translate("SceneEditorWidget", u"point", None))
        self.add_graphics_combobox.setItemText(3, QCoreApplication.translate("SceneEditorWidget", u"node points", None))
        self.add_graphics_combobox.setItemText(4, QCoreApplication.translate("SceneEditorWidget", u"data points", None))
        self.add_graphics_combobox.setItemText(5, QCoreApplication.translate("SceneEditorWidget", u"element points", None))
        self.add_graphics_combobox.setItemText(6, QCoreApplication.translate("SceneEditorWidget", u"lines", None))
        self.add_graphics_combobox.setItemText(7, QCoreApplication.translate("SceneEditorWidget", u"surfaces", None))
        self.add_graphics_combobox.setItemText(8, QCoreApplication.translate("SceneEditorWidget", u"contours", None))
        self.add_graphics_combobox.setItemText(9, QCoreApplication.translate("SceneEditorWidget", u"streamlines", None))

        self.delete_graphics_button.setText(QCoreApplication.translate("SceneEditorWidget", u"Delete", None))
    # retranslateUi

