"""
this is the front end
"""

import os

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTreeWidgetItem
from rdflib import Graph
from rdflib import Literal

from PeriConto import COLOURS
from PeriConto import LINK_COLOUR
from PeriConto import MYTerms
from PeriConto import ONTOLOGY_DIRECTORY
from PeriConto import PRIMITIVES
from PeriConto import PRIMITIVE_COLOUR
from PeriConto import RDFSTerms
from PeriConto import VALUE
from PeriConto import getData
from PeriConto import makeRDFCompatible
from PeriConto import plot
from PeriConto import saveWithBackup
# from graphHAP import Graph
from PeriContoCoatedProduct_gui import Ui_MainWindow
from resources.pop_up_message_box import makeMessageBox
from resources.resources_icons import roundButton
from resources.single_list_selector_impl import SingleListSelector
from resources.ui_string_dialog_impl import UI_String

from PeriContoCoatedProductBackEnd import BackEnd


def makeTree(truples, origin=[], stack=[], items={}):
  for s, o, p in truples:
    if (s, o, p) not in stack:
      if s != origin:
        if o in items:
          # print("add %s <-- %s" % (o, s),p)
          item = QTreeWidgetItem(items[o])
          # print("debugging -- color",p )
          item.setBackground(0, COLOURS[p])
          item.predicate = p
          stack.append((s, o, p))
          item.setText(0, s)
          items[s] = item
          makeTree(truples, origin=s, stack=stack, items=items)
          

class PeriContoPyQtFrontEnd(QMainWindow):
  def __init__(self):
    super(PeriContoPyQtFrontEnd, self).__init__()

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    self.gui_objects = {"buttons"  :
                          {"load"      : self.ui.pushLoad,
                           "create"    : self.ui.pushCreate,
                           "visualise" : self.ui.pushVisualise,
                           "save"      : self.ui.pushSave,
                           "exit"      : self.ui.pushExit,
                           "addChanges": self.ui.pushAddValueElucidation,
                            "AddValueElucidation_button": self.ui.pushAddValueElucidation,
                           },
                        "selectors": {
                                "classList"    : self.ui.listClasses,
                                "classTree": self.ui.treeClass,
                                },
                        "textEdit" : {
                                "textValue": self.ui.textValueElucidation,
                                "textClass": self.ui.textClassSubclassElucidation,
                                },
                        "lineEdit" : {
                                "stringIdentifier": self.ui.editString,
                                },
                        "groups"   : {
                                "ClassSubclassElucidation"  : self.ui.groupClassSubclassElucidation,
                                "ValueElucidation"          : self.ui.groupValueElucidation,
                                "PrimitiveString"           : self.ui.groupString,
                                "PrimitiveQuantity"         : self.ui.groupQuantityMeasure,
                                },
                        }

    self.gui_objects_events = {"buttons" : ["pressed"],
                               "selectors": ["picked"],
                               "textEdit": ["textChanged"],
                               "groups": [],
                               }

    self.gui_objects_controls = {"object" : ["show", "hide", "size"],
                               "selectors": ["populate", "clear"],
                               "textEdit": ["populate", "clear"],
                                 "lineEdit": ["populate", "clear"]
            }
    self.gui_objects_controls = {"buttons"  :
                          {"buttons"  :
                          {"load"      : {"hide": self.ui.pushLoad.hide,
                                          "show": self.ui.pushLoad.show,},
                           "create"    : self.ui.pushCreate,
                           "visualise" : self.ui.pushVisualise,
                           "save"      : self.ui.pushSave,
                           "exit"      : self.ui.pushExit,
                           "addChanges": self.ui.pushAddValueElucidation,
                            "AddValueElucidation_button": self.ui.pushAddValueElucidation,
                           },
                           },
                        "selectors": {
                                "classList"    : {"populate": self.ui.listClasses.addItems,
                                                  "clear": self.ui.listClasses.clear},
                                "classTree": {"populate": self.makeClassTree,},
                                },
                        "textEdit" : {
                                "textValue": self.ui.textValueElucidation,
                                "textClass": self.ui.textClassSubclassElucidation,
                                },
                        "lineEdit" : {
                                "stringIdentifier": self.ui.editString,
                                },
                        "groups"   : {
                                "ClassSubclassElucidation"  : self.ui.groupClassSubclassElucidation,
                                "ValueElucidation"          : self.ui.groupValueElucidation,
                                "AddValueElucidation_button": self.ui.pushAddValueElucidation,
                                "PrimitiveString"           : self.ui.groupString,
                                "PrimitiveQuantity"         : self.ui.groupQuantityMeasure,
                                },
                        "dialogues" : UI_String,
                        }


    roundButton(self.ui.pushLoad, "load", tooltip="load ontology")
    roundButton(self.ui.pushCreate, "plus", tooltip="create")
    roundButton(self.ui.pushVisualise, "dot_graph", tooltip="visualise ontology")
    roundButton(self.ui.pushSave, "save", tooltip="save ontology")
    roundButton(self.ui.pushExit, "exit", tooltip="exit")


    self.backEnd = BackEnd(self)

  # def processCallBack(self, call_back, *data):
  #   if call_back == "populate":
  #     self.populate(*data)


  def dialog(self, Event, prompt, placeholder_text,limiting_list, on_fail ):

    dialog = UI_String(prompt, placeholder_text, limiting_list)
    dialog.exec_()
    name = dialog.getText()
    if name:
      self.backEnd.processEvent(Event, name)
    elif on_fail != "close":
      print(">>> I do not know what to do")
    else:
      self.close()

  def on_pushCreate_pressed(self):
    self.backEnd.processEvent("create",{})
    
  def makeClassTree(self, truples, root):
    widget = self.ui.treeClass
    widget.clear()

    rootItem = QTreeWidgetItem(widget)
    widget.setColumnCount(1)
    rootItem.root = root
    rootItem.setText(0, root)
    rootItem.setSelected(True)
    rootItem.predicate = None
    widget.addTopLevelItem(rootItem)
    self.current_class = root
    makeTree(truples, origin=root, stack=[], items={root: rootItem})
    # self.__makeTree(origin=Literal(origin), subject_stack=[], parent=rootItem)
    widget.show()
    widget.expandAll()
    self.current_subclass = root
    self.backEnd.ui_state("show_tree")

    pass

  def populate(self, gui_class, gui_obj, *contents):
    self.gui_objects_controls[gui_class][gui_obj]["populate"](*contents)


  def on_listClasses_itemClicked(self, item):
    class_ID = item.text()
    # print("debugging -- ", class_ID)
    self.__shiftClass(class_ID)


  def __shiftClass(self, class_ID):
    self.backEnd.processEvent("shift_class", class_ID)
    self.current_class = class_ID
    self.__createTree(class_ID)
    if class_ID not in self.class_path:
      self.__addToClassPath(class_ID)
    else:
      self.__cutClassPath(class_ID)

if __name__ == "__main__":
  import sys

  app = QApplication(sys.argv)

  icon_f = "task_ontology_foundation.svg"
  icon = os.path.join(os.path.abspath("resources/icons"), icon_f)
  app.setWindowIcon(QtGui.QIcon(icon))

  MainWindow = PeriContoPyQtFrontEnd()
  MainWindow.show()
  sys.exit(app.exec_())
