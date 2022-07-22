#!/usr/bin/python3.5
# encoding: utf-8
# !/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 APP for constructing ontologies
===============================================================================


"""

__project__ = "VIPCOAT"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2009. 04. 17"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import os
import sys

from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets
#
# root = os.path.abspath(os.path.join(".."))
# sys.path.extend([root, os.path.join(root, 'packages'), os.path.join(root, 'tasks')])


from PeriConto_new import OntobuilderUI

a = QtWidgets.QApplication(sys.argv)

# icon_f = "task_automata.svg"
# icon = os.path.join(os.path.abspath("../packages/Common/icons"), icon_f)
# a.setWindowIcon(QtGui.QIcon(icon))

w = OntobuilderUI()
w.move(QtCore.QPoint(100, 100))
w.show()
a.exec_()
