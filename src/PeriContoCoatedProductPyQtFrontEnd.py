"""
this is the front end
"""

import os
from collections import OrderedDict

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTreeWidgetItem

from PeriContoCoatedProductBackEnd import BackEnd
# from graphHAP import Graph
from PeriContoCoatedProduct_gui import Ui_MainWindow
from resources.resources_icons import roundButton
from resources.ui_string_dialog_impl import UI_String

COLOURS = {
        "is_a_subclass_of": QtGui.QColor(0, 0, 0, 255),
        "link_to_class"   : QtGui.QColor(255, 100, 5, 255),
        "value"           : QtGui.QColor(155, 155, 255),
        "comment"         : QtGui.QColor(155, 155, 255),
        "integer"         : QtGui.QColor(155, 155, 255),
        "string"          : QtGui.QColor(255, 200, 200, 255),
        }

QBRUSHES = {"is_a_subclass_of": QtGui.QBrush(COLOURS["is_a_subclass_of"]),
            "link_to_class"   : QtGui.QBrush(COLOURS["link_to_class"]),
            "value"           : QtGui.QBrush(COLOURS["value"]),
            "comment"         : QtGui.QBrush(COLOURS["comment"]),
            "integer"         : QtGui.QBrush(COLOURS["integer"]),
            "string"          : QtGui.QBrush(COLOURS["string"]), }


def makeTree(truples, origin=[], stack=[], items={}):
  for s, o, p, graph_ID in truples:
    if (s, o) not in stack:
      if s != origin:
        if o in items:
          # print("add %s <-- %s" % (o, s),p)
          item = QTreeWidgetItem(items[o])
          item.setForeground(0,  QBRUSHES[p])
          item.subject = s
          item.object = o
          item.predicate = p
          item.graph_ID = graph_ID
          stack.append((s, o))
          item.setText(0, s)
          items[s] = item
          makeTree(truples, origin=s, stack=stack, items=items)


class PeriContoPyQtFrontEnd(QMainWindow):

  def __init__(self):
    super(PeriContoPyQtFrontEnd, self).__init__()

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    # Note: using an ordered dictionary is essential if groups are used in control being hidden/shown with contents.
    # group must be handled first and then all items including those being part of a group.

    self.gui_objects = OrderedDict()
    self.gui_objects["groups"] = {
            "ClassSubclassElucidation": self.ui.groupClassSubclassElucidation,
            "ValueElucidation"        : self.ui.groupValueElucidation,
            "PrimitiveString"         : self.ui.groupString,
            "integer"                 : self.ui.groupQuantityMeasure,
            "classList"               : self.ui.groupBoxClassList,
            "classTree"               : self.ui.groupBoxTree,
            }
    self.gui_objects["buttons"] = {"load"               : self.ui.pushLoad,
                                   "create"             : self.ui.pushCreate,
                                   "visualise"          : self.ui.pushVisualise,
                                   "save"               : self.ui.pushSave,
                                   "exit"               : self.ui.pushExit,
                                   "addChanges"         : self.ui.pushAddValueElucidation,
                                   "addValueElucidation": self.ui.pushAddValueElucidation,
                                   "instantiate"        : self.ui.pushInstantiate,
                                   }
    self.gui_objects["selectors"] = {
            "classList": self.ui.listClasses,
            "classTree": self.ui.treeClass,
            "integer"  : self.ui.spinNumber,
            }
    self.gui_objects["textEdit"] = {
            "textValue": self.ui.textValueElucidation,
            "textClass": self.ui.textClassSubclassElucidation,
            }
    self.gui_objects["lineEdit"] = {
            "stringIdentifier": self.ui.editString,
            }

    self.gui_objects_controls = {"buttons"  :
                                   {"load"               : {"hide": self.ui.pushLoad.hide,
                                                            "show": self.ui.pushLoad.show, },
                                    "create"             : {"hide": self.ui.pushCreate.hide,
                                                            "show": self.ui.pushCreate.show, },
                                    "visualise"          : {"hide": self.ui.pushVisualise.hide,
                                                            "show": self.ui.pushVisualise.show, },
                                    "save"               : {"hide": self.ui.pushSave.hide,
                                                            "show": self.ui.pushSave.show, },
                                    "exit"               : {"hide": self.ui.pushExit.hide,
                                                            "show": self.ui.pushExit.show, },
                                    "addChanges"         : {"hide": self.ui.pushAddValueElucidation.hide,
                                                            "show": self.ui.pushAddValueElucidation.show, },
                                    "addValueElucidation": {"hide": self.ui.pushAddValueElucidation.hide,
                                                            "show": self.ui.pushAddValueElucidation.show, },
                                    "instantiate"        : {"hide": self.ui.pushInstantiate.hide,
                                                            "show": self.ui.pushInstantiate.show}
                                    },
                                 "selectors": {
                                         "classList": {"populate": self.__populateListClass,
                                                       "hide"    : self.__hideClassList,
                                                       "show"    : self.__showClassList},
                                         # "hide": self.ui.listClasses.hide,
                                         # "show": self.ui.listClasses.show,}
                                         "classTree": {"populate": self.__makeClassTree,
                                                       "hide"    : self.__hideClassTree,
                                                       "show"    : self.__showClassTree, },

                                         "integer"  : {"hide": self.__hideInteger,
                                                       "show": self.__showInteger},
                                         # "hide": self.ui.treeClass.hide,
                                         # "show": self.ui.treeClass.show,},
                                         },
                                 "textEdit" : {
                                         "textValue": {"populate": self.__populateTextValueEdit,
                                                       "hide"    : self.ui.groupValueElucidation.hide,
                                                       "show"    : self.ui.groupValueElucidation.show},
                                         "textClass": {"populate": self.ui.textClassSubclassElucidation,
                                                       "hide"    : self.ui.textClassSubclassElucidation.hide,
                                                       "show"    : self.ui.textClassSubclassElucidation.show},
                                         },
                                 "lineEdit" : {
                                         "stringIdentifier": {"populate": self.__editIdentifier,
                                                              "hide"    : self.ui.groupString.hide,
                                                              "show"    : self.ui.groupString.show},
                                         },
                                 "groups"   : {
                                         "ClassSubclassElucidation": {
                                                 "show": self.ui.groupClassSubclassElucidation.show,
                                                 "hide": self.ui.groupClassSubclassElucidation.hide},
                                         "ValueElucidation"        : {"show": self.ui.groupValueElucidation.show,
                                                                      "hide": self.ui.groupValueElucidation.hide},
                                         "addValueElucidation"     : {"show": self.ui.pushAddValueElucidation.show,
                                                                      "hide": self.ui.pushAddValueElucidation.hide},
                                         "PrimitiveString"         : {"show": self.ui.groupString.show,
                                                                      "hide": self.ui.groupString.hide},
                                         "integer"                 : {"show": self.ui.groupQuantityMeasure.show,
                                                                      "hide": self.ui.groupQuantityMeasure.hide},
                                         "classList"               : {"show": self.ui.groupBoxClassList.show,
                                                                      "hide": self.ui.groupBoxClassList.hide},
                                         "classTree"               : {"show": self.ui.groupBoxTree.show,
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

  def dialog(self, state, Event, prompt, placeholder_text, limiting_list, on_fail):

    dialog = UI_String(prompt, placeholder_text, limiting_list)
    dialog.exec_()
    name = dialog.getText()
    if name:
      self.backEnd.processEvent(state, Event, name)
    elif on_fail != "close":
      print(">>> I do not know what to do")
    else:
      self.close()

  def fileNameDialog(self, state, Event, prompt, directory, type, on_fail):
    name = QFileDialog.getOpenFileName(None,
                                       prompt,
                                       directory,
                                       type,
                                       )[0]

    if name:
      self.backEnd.processEvent(state, Event, name)
    elif on_fail != "close":
      print(">>> I do not know what to do")
    else:
      self.close()

  def on_pushCreate_pressed(self):
    self.backEnd.processEvent("initialised", "create", None)

  def on_pushLoad_pressed(self):
    self.backEnd.processEvent("load", )

  def __makeClassTree(self, truples, root):
    widget = self.ui.treeClass
    widget.clear()

    rootItem = QTreeWidgetItem(widget)
    widget.setColumnCount(1)
    rootItem.root = root
    rootItem.setText(0, root)
    rootItem.setSelected(True)
    rootItem.subject = None
    rootItem.object = root
    rootItem.predicate = None
    rootItem.graph_ID = root
    widget.addTopLevelItem(rootItem)
    self.current_class = root
    makeTree(truples, origin=root, stack=[], items={root: rootItem})
    widget.show()
    widget.expandAll()
    self.current_subclass = root
    pass

  def __buttonShow(self, show):
    for b in self.gui_objects["buttons"]:
      self.gui_objects["buttons"][b].hide()
    for b in show:
      self.gui_objects["buttons"][b].hide()

  #
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

  def __showInteger(self):
    self.gui_objects["selectors"]["integer"].show()
    self.gui_objects["groups"]["classList"].show()

  def __hideInteger(self):
    self.gui_objects["selectors"]["integer"].hide()
    self.gui_objects["groups"]["classList"].hide()

  def controls(self, gui_class, gui_obj, action, *contents):
    # if gui_obj == "instantiate":
    #   print("debugging -- controls", gui_class, gui_obj, action, *contents)
    self.gui_objects_controls[gui_class][gui_obj][action](*contents)

  def on_listClasses_itemClicked(self, item):
    class_ID = item.text()
    print("debugging -- ", class_ID)
    self.backEnd.processEvent("class_list_clicked", "selected", class_ID)

  def on_treeClass_itemPressed(self, item, column):
    text_ID = item.text(column)
    self.triple = (item.subject, item.predicate, item.object)
    subject = item.subject
    object = item.object
    predicate = item.predicate
    graph_ID = item.graph_ID
    print("FrontEnd -- debugging selected item:", text_ID, subject, predicate, object)
    self.backEnd.processEvent("show_tree", "selected", [subject, predicate, object,  graph_ID])

  def on_pushInstantiate_pressed(self):
    self.backEnd.processEvent("wait_for_ID", "add_new_ID",self.triple)

if __name__ == "__main__":
  import sys

  app = QApplication(sys.argv)

  icon_f = "task_ontology_foundation.svg"
  icon = os.path.join(os.path.abspath("resources/icons"), icon_f)
  app.setWindowIcon(QtGui.QIcon(icon))

  MainWindow = PeriContoPyQtFrontEnd()
  MainWindow.show()
  sys.exit(app.exec_())
