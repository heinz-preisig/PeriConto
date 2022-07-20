# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'single_list_selector.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.setWindowModality(QtCore.Qt.NonModal)
        Dialog.resize(503, 257)
        self.listWidget = QtWidgets.QListWidget(Dialog)
        self.listWidget.setGeometry(QtCore.QRect(10, 90, 321, 111))
        self.listWidget.setObjectName("listWidget")
        self.layoutWidget = QtWidgets.QWidget(Dialog)
        self.layoutWidget.setGeometry(QtCore.QRect(10, 10, 242, 71))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout.setSizeConstraint(QtWidgets.QLayout.SetMinAndMaxSize)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushLeft = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushLeft.sizePolicy().hasHeightForWidth())
        self.pushLeft.setSizePolicy(sizePolicy)
        self.pushLeft.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.pushLeft.setText("")
        self.pushLeft.setIconSize(QtCore.QSize(60, 60))
        self.pushLeft.setAutoDefault(False)
        self.pushLeft.setObjectName("pushLeft")
        self.horizontalLayout.addWidget(self.pushLeft)
        self.pushRight = QtWidgets.QPushButton(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushRight.sizePolicy().hasHeightForWidth())
        self.pushRight.setSizePolicy(sizePolicy)
        self.pushRight.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.pushRight.setText("")
        self.pushRight.setIconSize(QtCore.QSize(60, 60))
        self.pushRight.setAutoDefault(False)
        self.pushRight.setObjectName("pushRight")
        self.horizontalLayout.addWidget(self.pushRight)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.listWidget.setSortingEnabled(True)
        self.pushLeft.setToolTip(_translate("Dialog", "exit dialog"))
        self.pushRight.setToolTip(_translate("Dialog", "accept selection"))
