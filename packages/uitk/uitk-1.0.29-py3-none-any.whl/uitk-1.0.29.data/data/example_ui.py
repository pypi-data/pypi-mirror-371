# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'example.ui'
##
## Created by: Qt User Interface Compiler version 6.9.1
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QGridLayout, QGroupBox,
    QMainWindow, QSizePolicy, QTabWidget, QTextEdit,
    QVBoxLayout, QWidget)

from uitk.widgets.header.Header import Header
from widgets.doublespinbox import DoubleSpinBox
from widgets.pushbutton import PushButton

class Ui_QtUi(object):
    def setupUi(self, QtUi):
        if not QtUi.objectName():
            QtUi.setObjectName(u"QtUi")
        QtUi.setEnabled(True)
        QtUi.resize(200, 300)
        QtUi.setTabShape(QTabWidget.Triangular)
        QtUi.setDockNestingEnabled(True)
        QtUi.setDockOptions(QMainWindow.AllowNestedDocks|QMainWindow.AllowTabbedDocks|QMainWindow.AnimatedDocks|QMainWindow.ForceTabbedDocks)
        self.central_widget = QWidget(QtUi)
        self.central_widget.setObjectName(u"central_widget")
        self.central_widget.setMinimumSize(QSize(200, 130))
        self.verticalLayout = QVBoxLayout(self.central_widget)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout_1 = QVBoxLayout()
        self.verticalLayout_1.setSpacing(1)
        self.verticalLayout_1.setObjectName(u"verticalLayout_1")
        self.header = Header(self.central_widget)
        self.header.setObjectName(u"header")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.header.sizePolicy().hasHeightForWidth())
        self.header.setSizePolicy(sizePolicy)
        self.header.setMinimumSize(QSize(0, 20))
        self.header.setMaximumSize(QSize(16777215, 20))
        font = QFont()
        font.setBold(True)
        self.header.setFont(font)

        self.verticalLayout_1.addWidget(self.header)

        self.groupBox = QGroupBox(self.central_widget)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(self.groupBox)
        self.gridLayout.setSpacing(2)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.button_a = PushButton(self.groupBox)
        self.button_a.setObjectName(u"button_a")
        self.button_a.setMinimumSize(QSize(0, 20))
        self.button_a.setMaximumSize(QSize(999, 20))
        self.button_a.setLayoutDirection(Qt.RightToLeft)
        self.button_a.setAutoDefault(False)
        self.button_a.setFlat(False)
        self.button_a.setProperty(u"bnabled", True)

        self.gridLayout.addWidget(self.button_a, 0, 0, 1, 1)

        self.checkbox = QCheckBox(self.groupBox)
        self.checkbox.setObjectName(u"checkbox")

        self.gridLayout.addWidget(self.checkbox, 1, 0, 1, 1)

        self.button_b = PushButton(self.groupBox)
        self.button_b.setObjectName(u"button_b")
        self.button_b.setMinimumSize(QSize(0, 20))
        self.button_b.setMaximumSize(QSize(999, 20))
        self.button_b.setLayoutDirection(Qt.RightToLeft)
        self.button_b.setAutoDefault(False)
        self.button_b.setFlat(False)
        self.button_b.setProperty(u"bnabled", True)

        self.gridLayout.addWidget(self.button_b, 0, 2, 1, 1)

        self.spinbox = DoubleSpinBox(self.groupBox)
        self.spinbox.setObjectName(u"spinbox")

        self.gridLayout.addWidget(self.spinbox, 1, 2, 1, 1)


        self.verticalLayout_1.addWidget(self.groupBox)

        self.textedit = QTextEdit(self.central_widget)
        self.textedit.setObjectName(u"textedit")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.textedit.sizePolicy().hasHeightForWidth())
        self.textedit.setSizePolicy(sizePolicy1)
        self.textedit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.verticalLayout_1.addWidget(self.textedit)


        self.verticalLayout.addLayout(self.verticalLayout_1)

        QtUi.setCentralWidget(self.central_widget)

        self.retranslateUi(QtUi)

        self.button_a.setDefault(False)
        self.button_b.setDefault(False)


        QMetaObject.connectSlotsByName(QtUi)
    # setupUi

    def retranslateUi(self, QtUi):
        self.header.setText(QCoreApplication.translate("QtUi", u"EXAMPLE", None))
        self.groupBox.setTitle(QCoreApplication.translate("QtUi", u"GroupBox", None))
        self.button_a.setText(QCoreApplication.translate("QtUi", u"Button A", None))
        self.checkbox.setText(QCoreApplication.translate("QtUi", u"CheckBox", None))
        self.button_b.setText(QCoreApplication.translate("QtUi", u"Button B", None))
        self.textedit.setHtml(QCoreApplication.translate("QtUi", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'MS Shell Dlg 2'; font-size:7.85455pt; font-weight:400; font-style:normal;\">\n"
"<p align=\"center\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:7.85455pt; text-decoration: underline;\">TextEdit</span></p></body></html>", None))
        pass
    # retranslateUi

