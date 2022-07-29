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
                                "classList": self.ui.groupBoxClassList,
                                "classTree": self.ui.groupBoxTree},
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
                          {"load"      : {"hide": self.ui.pushLoad.hide,
                                          "show": self.ui.pushLoad.show,},
                           "create"    : {"hide": self.ui.pushCreate.hide,
                                          "show": self.ui.pushCreate.show,},
                           "visualise" : {"hide": self.ui.pushVisualise.hide,
                                          "show": self.ui.pushVisualise.show,},
                           "save"      : {"hide": self.ui.pushSave.hide,
                                          "show": self.ui.pushSave.show,},
                           "exit"      : {"hide": self.ui.pushExit.hide,
                                          "show": self.ui.pushExit.show,},
                           "addChanges": {"hide": self.ui.pushAddValueElucidation.hide,
                                          "show": self.ui.pushAddValueElucidation.show,},
                            "AddValueElucidation_button": {"hide": self.ui.pushAddValueElucidation.hide,
                                          "show": self.ui.pushAddValueElucidation.show,},
                           },
                        "selectors": {
                                "classList"    : {"populate": self.__populateListClass,
                                                  "hide": self.__hideClassList,
                                                  "show": self.__showClassList},
                                "classTree": {"populate": self.__makeClassTree,
                                                  "hide": self.__hideClassTree,
                                                  "show": self.__showClassTree},
                                },
                        "textEdit" : {
                                "textValue": {"populate": self.__populateTextValueEdit,
                                                  "hide": self.ui.groupValueElucidation.hide,
                                                  "show": self.ui.groupValueElucidation.show},
                                "textClass": {"populate": self.ui.textClassSubclassElucidation,
                                                  "hide": self.ui.textClassSubclassElucidation.hide,
                                                  "show": self.ui.textClassSubclassElucidation.show},
                                },
                        "lineEdit" : {
                                "stringIdentifier": {"populate": self.__editIdentifier,
                                               "hide": self.ui.groupString.hide,
                                               "show": self.ui.groupString.show},
                                },
                        "groups"   : {
                                "ClassSubclassElucidation"  : {"show": self.ui.groupClassSubclassElucidation.show,
                                                               "hide": self.ui.groupClassSubclassElucidation.hide},
                                "ValueElucidation"          : {"show": self.ui.groupValueElucidation.show,
                                                               "hide": self.ui.groupValueElucidation.hide},
                                "AddValueElucidation_button": {"show": self.ui.pushAddValueElucidation.show,
                                                               "hide": self.ui.pushAddValueElucidation.hide},
                                "PrimitiveString"           : {"show": self.ui.groupString.show,
                                                               "hide": self.ui.groupString.hide},
                                "PrimitiveQuantity"         : {"show": self.ui.groupQuantityMeasure.show,
                                                               "hide": self.ui.groupQuantityMeasure.hide},
                                "classList":                  {"show": self.ui.groupBoxClassList.show,
                                                               "hide": self.ui.groupBoxClassList.hide},
                                "classTree"                 : {"show": self.ui.groupBoxTree.show,
                                                               "hide": self.ui.groupBoxTree.hide},
                                },
                        # "dialogues" : UI_String,
                        }

    roundButton(self.ui.pushLoad, "load", tooltip="load ontology")
    roundButton(self.ui.pushCreate, "plus", tooltip="create")
    roundButton(self.ui.pushVisualise, "dot_graph", tooltip="visualise ontology")
    roundButton(self.ui.pushSave, "save", tooltip="save ontology")
    roundButton(self.ui.pushExit, "exit", tooltip="exit")


    self.backEnd = BackEnd(self)



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

  def fileNameDialog(self, Event, prompt, directory, type, on_fail):
    name = QFileDialog.getOpenFileName(None,
                                         prompt,
                                         directory,
                                         type,
                                         )[0]

    if name:
      self.backEnd.processEvent(Event, name)
    elif on_fail != "close":
      print(">>> I do not know what to do")
    else:
      self.close()

  def on_pushCreate_pressed(self):
    self.backEnd.processEvent("create",{})

  def on_pushLoad_pressed(self):
    self.backEnd.processEvent("load", {})
    
  def __makeClassTree(self, truples, root):
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
    self.gui_objects_controls["selectors"]["classTree"]["show"]()
    # self.backEnd.ui_state("show_tree")
    pass

  def __buttonShow(self, show):
    for b in self.gui_objects["buttons"]:
      self.gui_objects["buttons"][b].hide()
    for b in show:
      self.gui_objects["buttons"][b].hide()

  def __showClassList(self):
    self.gui_objects["selectors"]["classList"].show()
    self.gui_objects["groups"]["classList"].show()

  def __hideClassList(self):
    self.gui_objects["selectors"]["classList"].hide()
    self.gui_objects["groups"]["classList"].hide()

  def __showClassTree(self):
    self.gui_objects["selectors"]["classTree"].show()
    self.gui_objects["groups"]["classTree"].show()

  def __hideClassTree(self):
    self.gui_objects["selectors"]["classTree"].hide()
    self.gui_objects["groups"]["classTree"].hide()

  def __populateListClass(self, data):
    self.gui_objects["selectors"]["classList"].clear()
    self.gui_objects["selectors"]["classList"].addItems(data)
    self.gui_objects["groups"]["classList"].show()
    self.gui_objects["selectors"]["classList"].show()

  def __populateTextValueEdit(self, data):
    self.gui_objects["textEdit"]["textValue"].clear()
    self.gui_objects["textEdit"]["textValue"].setPlainText(data)

  def __populateClassSubclassElucidation(self, data):
    self.gui_objects["textEdit"]["textValue"].clear()
    self.gui_objects["textClass"]["textValue"].setPlainText(data)

  def __editIdentifier(self, data):
    self.gui_objects_controls["lineEdit"]["identifier"].clear()
    self.gui_objects_controls["lineEdit"]["identifier"].setText(data)


  def controls(self, gui_class, gui_obj, action, *contents):
    self.gui_objects_controls[gui_class][gui_obj][action](*contents)

  def on_listClasses_itemClicked(self, item):
    class_ID = item.text()
    # print("debugging -- ", class_ID)
    self.backEnd.processEvent("selected_class", class_ID)


  def on_treeClass_itemPressed(self, item, column):

    item = self.ui.treeClass.selectedItems()[0]

    column = 0
    text_ID = item.text(column)

if __name__ == "__main__":
  import sys

  app = QApplication(sys.argv)

  icon_f = "task_ontology_foundation.svg"
  icon = os.path.join(os.path.abspath("resources/icons"), icon_f)
  app.setWindowIcon(QtGui.QIcon(icon))

  MainWindow = PeriContoPyQtFrontEnd()
  MainWindow.show()
  sys.exit(app.exec_())
