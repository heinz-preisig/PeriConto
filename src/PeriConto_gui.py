# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'PeriConto_gui.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1593, 808)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.groupBoxTree = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBoxTree.setGeometry(QtCore.QRect(300, 140, 761, 551))
        self.groupBoxTree.setObjectName("groupBoxTree")
        self.treeClass = QtWidgets.QTreeWidget(self.groupBoxTree)
        self.treeClass.setGeometry(QtCore.QRect(10, 31, 521, 401))
        self.treeClass.setAutoExpandDelay(1)
        self.treeClass.setColumnCount(0)
        self.treeClass.setObjectName("treeClass")
        self.treeClass.header().setVisible(False)
        self.treeClass.header().setCascadingSectionResizes(False)
        self.groupBoxEditor = QtWidgets.QGroupBox(self.groupBoxTree)
        self.groupBoxEditor.setGeometry(QtCore.QRect(10, 450, 951, 91))
        self.groupBoxEditor.setObjectName("groupBoxEditor")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.groupBoxEditor)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 30, 721, 51))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushAddSubclass = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushAddSubclass.setObjectName("pushAddSubclass")
        self.horizontalLayout.addWidget(self.pushAddSubclass)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushAddPrimitive = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushAddPrimitive.setObjectName("pushAddPrimitive")
        self.horizontalLayout.addWidget(self.pushAddPrimitive)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pushAddExistingClass = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushAddExistingClass.setObjectName("pushAddExistingClass")
        self.horizontalLayout.addWidget(self.pushAddExistingClass)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem2)
        self.pushAddNewClass = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushAddNewClass.setObjectName("pushAddNewClass")
        self.horizontalLayout.addWidget(self.pushAddNewClass)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem3)
        self.pushRemoveNode = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushRemoveNode.setObjectName("pushRemoveNode")
        self.horizontalLayout.addWidget(self.pushRemoveNode)
        self.groupBoxClassList = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBoxClassList.setGeometry(QtCore.QRect(20, 140, 261, 551))
        self.groupBoxClassList.setObjectName("groupBoxClassList")
        self.listClasses = QtWidgets.QListWidget(self.groupBoxClassList)
        self.listClasses.setGeometry(QtCore.QRect(5, 40, 251, 481))
        self.listClasses.setObjectName("listClasses")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(100, 20, 495, 80))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.pushLoad = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pushLoad.setObjectName("pushLoad")
        self.horizontalLayout_2.addWidget(self.pushLoad)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem4)
        self.pushCreate = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pushCreate.setObjectName("pushCreate")
        self.horizontalLayout_2.addWidget(self.pushCreate)
        spacerItem5 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem5)
        self.pushVisualise = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pushVisualise.setObjectName("pushVisualise")
        self.horizontalLayout_2.addWidget(self.pushVisualise)
        spacerItem6 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem6)
        self.pushSave = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pushSave.setObjectName("pushSave")
        self.horizontalLayout_2.addWidget(self.pushSave)
        spacerItem7 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem7)
        self.pushExit = QtWidgets.QPushButton(self.horizontalLayoutWidget_2)
        self.pushExit.setObjectName("pushExit")
        self.horizontalLayout_2.addWidget(self.pushExit)
        self.groupElucidation = QtWidgets.QGroupBox(self.centralwidget)
        self.groupElucidation.setGeometry(QtCore.QRect(1079, 140, 461, 551))
        self.groupElucidation.setObjectName("groupElucidation")
        self.pushAddElucidation = QtWidgets.QPushButton(self.groupElucidation)
        self.pushAddElucidation.setGeometry(QtCore.QRect(30, 490, 101, 23))
        self.pushAddElucidation.setObjectName("pushAddElucidation")
        self.textElucidation = QtWidgets.QPlainTextEdit(self.groupElucidation)
        self.textElucidation.setGeometry(QtCore.QRect(10, 30, 441, 401))
        self.textElucidation.setObjectName("textElucidation")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.groupBoxTree.setTitle(_translate("MainWindow", "ontology tree"))
        self.groupBoxEditor.setTitle(_translate("MainWindow", "ontology editor"))
        self.pushAddSubclass.setText(_translate("MainWindow", "add subclass"))
        self.pushAddPrimitive.setText(_translate("MainWindow", "add primitive"))
        self.pushAddExistingClass.setText(_translate("MainWindow", "add existing class"))
        self.pushAddNewClass.setText(_translate("MainWindow", "add new class"))
        self.pushRemoveNode.setText(_translate("MainWindow", "remove node"))
        self.groupBoxClassList.setTitle(_translate("MainWindow", "class list"))
        self.pushLoad.setText(_translate("MainWindow", "PushButton"))
        self.pushCreate.setText(_translate("MainWindow", "PushButton"))
        self.pushVisualise.setText(_translate("MainWindow", "PushButton"))
        self.pushSave.setText(_translate("MainWindow", "PushButton"))
        self.pushExit.setText(_translate("MainWindow", "PushButton"))
        self.groupElucidation.setTitle(_translate("MainWindow", "selection elucidation"))
        self.pushAddElucidation.setText(_translate("MainWindow", "add changes"))
