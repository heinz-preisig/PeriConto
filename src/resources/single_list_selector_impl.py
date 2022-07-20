#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 graph object resources
===============================================================================

The graph objects are used in the ModelComposer and defined based on a basic structure stored in
gaph_objects_ini.json
and edited in GraphComponentenEditor
"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2013. 01. 09"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

from copy import copy

from PyQt5 import QtCore
from PyQt5 import QtWidgets

from resources.resources_icons import roundButton
from resources.single_list_selector import Ui_Dialog


class SingleListSelector(QtWidgets.QDialog):
  '''
  selects an item from a list
  '''

  newSelection = QtCore.pyqtSignal(str)

  def __init__(self, thelist, selected=None, myparent=None, left_icon="reject", left_tooltip="reject",
               right_icon="accept", right_tooltip="accept"):
    '''
    Constructor
    Behaviour
     -- double click assumes also right button pressed
     -- single click requires acceptance -- default right button
     -- left button is default reject
     -- returns selection and state (left | right | selected)
    '''
    self.thelist = thelist
    self.selection = None
    QtWidgets.QDialog.__init__(self, parent=myparent)
    self.ui = Ui_Dialog()
    self.ui.setupUi(self)


    roundButton(self.ui.pushLeft, left_icon, left_tooltip )
    roundButton(self.ui.pushRight, right_icon, right_tooltip )

    self.ui.listWidget.addItems(thelist)

    self.selection = None
    self.state = None  # left | right | selected

    max_width = 0
    height = 20
    for i in thelist:
      label = QtWidgets.QLabel(i)
      width = label.fontMetrics().boundingRect(label.text()).width()
      height = height + label.fontMetrics().boundingRect(label.text()).height()
      if width > max_width:
        max_width = width
    self.__resizeMe(height, max_width + 20)

    # self.__move2row(selected)
    # if not left_icon:
    #   self.ui.pushLeft.hide()
    # else:
    #   self.ui.pushLeft.show()
    # self.ui.pushRight.hide()
    #
    # if not thelist:
    #   self.ui.listWidget.hide()
    #
    # self.hide()

  def __move2row(self, selected):
    if (selected != None) and (selected in self.thelist):
      row = self.thelist.index(selected)
      self.ui.listWidget.setCurrentRow(row)
      self.selection = copy(selected)
    else:
      row = -1
      self.ui.pushLeft.hide()
    self.ui.listWidget.setCurrentRow(row)

  def Show(self, entry):
    self.__move2row(entry)
    QtWidgets.QDialog.show(self)

  def hide(self):
    QtWidgets.QWidget.hide(self)

  def getSelection(self):
    return self.selection

  def __resizeMe(self, height, width):
    tab_size = QtCore.QSize(width, height)
    self.ui.listWidget.resize(tab_size)
    size_b = self.ui.pushLeft.size()
    b_width = size_b.width()* 2 #there are two buttons plus margin
    b_height = size_b.height()
    if b_width < width:
      size_b.setWidth(width)
    elif width < b_width:
      width = b_width
      tab_size = QtCore.QSize(width, height)
      self.ui.listWidget.resize(tab_size)
    s = QtCore.QSize(width + 20, b_height + height + 60)
    self.resize(s)

  def on_listWidget_itemClicked(self, v):
    # print('item clicked')
    currentItem = self.ui.listWidget.currentItem()
    self.selection = str(currentItem.text())
    self.state = "selected"
    self.ui.pushRight.show()

  def on_listWidget_itemDoubleClicked(self, v):
    self.on_listWidget_itemClicked(v)
    self.state = "selected"
    self.on_pushRight_pressed()

  def on_pushRight_pressed(self):
    # self.newSelection.emit(str(self.selection))
    self.state = "right"
    self.newSelection.emit(self.selection)
    self.hide()

  def on_pushLeft_pressed(self):
    self.state = "left"
    self.selection = None
    self.hide()

  def accept(self):  # overwrite dialogue method
    # print('accept', self.selection)
    self.hide()

  def reject(self):  # overwrite dialogue method
    print('reject', self.selection)
    self.hide()
    return
