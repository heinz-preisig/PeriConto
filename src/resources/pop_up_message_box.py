#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 Ontology design facility
===============================================================================

This program is part of the ProcessModelling suite

"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "11.11.2019"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "5.04"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import sys

from PyQt5 import QtWidgets, QtCore

BUTTONS = {
        "OK"             : QtWidgets.QMessageBox.Ok,
        "NO"             : QtWidgets.QMessageBox.No,
        "YES"             : QtWidgets.QMessageBox.Yes,
        "open"           : QtWidgets.QMessageBox.Open,
        "save"           : QtWidgets.QMessageBox.Save,
        "cancel"         : QtWidgets.QMessageBox.Cancel,
        "close"          : QtWidgets.QMessageBox.Close,
        "discard"        : QtWidgets.QMessageBox.Discard,
        "apply"          : QtWidgets.QMessageBox.Apply,
        "reset"          : QtWidgets.QMessageBox.Reset,
        "restore_default": QtWidgets.QMessageBox.RestoreDefaults,
        "help"           : QtWidgets.QMessageBox.Help,
        "save_all"       : QtWidgets.QMessageBox.SaveAll,
        "yes"            : QtWidgets.QMessageBox.Yes,
        "yes_to_all"     : QtWidgets.QMessageBox.YesToAll,
        "no"             : QtWidgets.QMessageBox.No,
        "no_to_all"      : QtWidgets.QMessageBox.NoToAll,
        "abort"          : QtWidgets.QMessageBox.Abort,
        "retry"          : QtWidgets.QMessageBox.Retry,
        "ignore"         : QtWidgets.QMessageBox.Ignore,
        "no button"      : QtWidgets.QMessageBox.NoButton,
        }


def makeMessageBox(message, buttons=["cancel", "OK"], infotext=""):
  """
  Buttons[0] is set as default
  """
  msg_box = QtWidgets.QMessageBox()
  msg_box.setText(message)
  msg_box.setInformativeText(infotext)
  msg_box.setWindowTitle("dialog")
  msg_box.setWindowFlags( QtCore.Qt.CustomizeWindowHint |QtCore.Qt.Popup)

  # save = QtWidgets.QMessageBox.Save
  # discard = QtWidgets.QMessageBox.Discard
  # cancel = QtWidgets.QMessageBox.Cancel
  mybuttons = BUTTONS[buttons[0]]
  for buts in buttons:
    mybuttons = mybuttons | BUTTONS[buts]

  msg_box.setStandardButtons(mybuttons)  # discard | save | cancel);
  msg_box.setDefaultButton(BUTTONS[buttons[0]])
  msg_box.show()
  r = msg_box.exec_()

  for i in BUTTONS:
    if r == BUTTONS[i]:
      return i

  return None


if __name__ == '__main__':
  a = QtWidgets.QApplication(sys.argv)
  s = makeMessageBox("hello this is a very long message  even longer than one expcts \n hello",
                     infotext="gugus")
  print(s)
  sys.exit()
