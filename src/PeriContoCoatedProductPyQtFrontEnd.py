"""
this is the front end
"""

import os
from collections import OrderedDict

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QTreeWidgetItem

# from PeriContoCoatedProductRDFBackEnd import BackEnd
# from PeriContoCoatedProductRDFBackEnd import DELIMITERS
from PeriContoCoatedProductTreeBackEnd import BackEnd
from PeriContoCoatedProductTreeBackEnd import DELIMITERS
from PeriContoCoatedProductTree_gui import Ui_MainWindow
from resources.pop_up_message_box import makeMessageBox
from resources.resources_icons import roundButton
from resources.ui_string_dialog_impl import UI_String

# from graphHAP import Graph

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


def makeTree(objTree, node_id, rootItem):
  stack = [node_id]
  items = {node_id: rootItem}
  while stack:
    node_id = stack[0]
    stack = stack[1:]
    # node_id = objTree["IDs"][node_id]
    children_ids = objTree["tree"].getChildren(node_id)
    for child_id in children_ids:
      items[child_id] = QTreeWidgetItem(items[node_id])
      child_tag = objTree["nodes"][child_id]
      items[child_id].setText(0, child_tag)
      items[child_id].reversed_path = objTree["tree"].getAncestors(child_id)
      items[child_id].node_id = node_id
      # print("building tree", child_id, objTree["tree"].getAncestors(child_id) )
      stack.insert(0, child_id)

  print("debugging -- finished")

  #   if o == origin:
  #         # print("add %s <-- %s" % (o, s),p)
  #       item = QTreeWidgetItem(items[o])
  #       item.setForeground(0, QBRUSHES[p])
  #       item.subject = s
  #       item.object = o
  #       item.predicate = p
  #       item.graph_ID = graph_ID
  #       # stack.append((s, o))
  #       item.setText(0, s)
  #       items[s] = item
  #       if (s,o) not in stack:
  #         makeTree(truples, origin=s, stack=stack, items=items)
  # if o == origin:
  #   stack.append((s,o))

  # for s, o, p, graph_ID in truples:
  #   if (s, o) not in stack:
  #     if s != origin:
  #       if o in items:
  #         # print("add %s <-- %s" % (o, s),p)
  #         item = QTreeWidgetItem(items[o])
  #         item.setForeground(0, QBRUSHES[p])
  #         item.subject = s
  #         item.object = o
  #         item.predicate = p
  #         item.graph_ID = graph_ID
  #         stack.append((s, o))
  #         item.setText(0, s)
  #         items[s] = item
  #         makeTree(truples, origin=s, stack=stack, items=items)


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
            "string"                  : self.ui.groupString,
            "integer"                 : self.ui.groupQuantityMeasure,
            "classList"               : self.ui.groupBoxClassList,
            "classTree"               : self.ui.groupBoxTree,
            }
    self.gui_objects["buttons"] = {"load"               : self.ui.pushLoad,
                                   "create"             : self.ui.pushCreate,
                                   "visualise"          : self.ui.pushVisualise,
                                   "save"               : self.ui.pushSave,
                                   "exit"               : self.ui.pushExit,
                                   # "addChanges"         : self.ui.pushAddValueElucidation,
                                   "addValueElucidation": self.ui.pushAcceptValueElucidation,
                                   "instantiate"        : self.ui.pushInstantiate,
                                   "acceptInteger"      : self.ui.pushAcceptInteger,
                                   "acceptString"       : self.ui.pushAcceptString,
                                   }
    self.gui_objects["selectors"] = {"classList": self.ui.listClasses,
                                     "classTree": self.ui.treeClass,
                                     "integer"  : self.ui.spinNumber,
                                     "string"   : self.ui.editString,
                                     "textValue": self.ui.textValueElucidation,
                                     "textClass": self.ui.textClassSubclassElucidation,
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
                                    # "addChanges"         : {"hide": self.ui.pushAddValueElucidation.hide,
                                    #                         "show": self.ui.pushAddValueElucidation.show, },
                                    "addValueElucidation": {"hide": self.ui.pushAcceptValueElucidation.hide,
                                                            "show": self.ui.pushAcceptValueElucidation.show, },
                                    "instantiate"        : {"hide": self.ui.pushInstantiate.hide,
                                                            "show": self.ui.pushInstantiate.show},
                                    "acceptInteger"      : {"hide": self.ui.pushAcceptInteger.hide,
                                                            "show": self.ui.pushAcceptInteger.show},
                                    "acceptString"       : {"hide": self.ui.pushAcceptString.hide,
                                                            "show": self.ui.pushAcceptString.show},
                                    },
                                 "selectors": {
                                         "classList": {"populate": self.__populateListClass,
                                                       "clear"   : self.ui.listClasses.clear,
                                                       "hide"    : self.__hideClassList,
                                                       "show"    : self.__showClassList},
                                         "classTree": {"populate": self.__makeClassTree,
                                                       "clear"   : self.ui.treeClass.clear,
                                                       "hide"    : self.__hideClassTree,
                                                       "show"    : self.__showClassTree, },
                                         "integer"  : {"populate": self.__populateInteger,
                                                       "clear"   : self.ui.spinNumber.clear,
                                                       "hide"    : self.__hideInteger,
                                                       "show"    : self.__showInteger},
                                         "textValue": {"populate": self.__populateTextValueEdit,
                                                       "clear"   : self.ui.editString.clear,
                                                       "hide"    : self.ui.groupValueElucidation.hide,
                                                       "show"    : self.ui.groupValueElucidation.show},
                                         "textClass": {"populate": self.ui.textClassSubclassElucidation,
                                                       "clear"   : self.ui.textClassSubclassElucidation.clear,
                                                       "hide"    : self.ui.textClassSubclassElucidation.hide,
                                                       "show"    : self.ui.textClassSubclassElucidation.show},
                                         "string"   : {"populate": self.__editIdentifier,
                                                       "clear"   : self.ui.editString.clear,
                                                       "hide"    : self.ui.editString.hide,
                                                       "show"    : self.ui.editString.show},
                                         },
                                 "groups"   : {
                                         "ClassSubclassElucidation": {
                                                 "show": self.ui.groupClassSubclassElucidation.show,
                                                 "hide": self.ui.groupClassSubclassElucidation.hide},
                                         "ValueElucidation"        : {"show": self.ui.groupValueElucidation.show,
                                                                      "hide": self.ui.groupValueElucidation.hide},
                                         "addValueElucidation"     : {"show": self.ui.pushAcceptValueElucidation.show,
                                                                      "hide": self.ui.pushAcceptValueElucidation.hide},
                                         "string"                  : {"show": self.ui.groupString.show,
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
    roundButton(self.ui.pushAcceptInteger, "accept", tooltip="accept integer")
    roundButton(self.ui.pushAcceptString, "accept", tooltip="accept string")
    roundButton(self.ui.pushAcceptValueElucidation, "accept", tooltip="accept text")

    self.backEnd = BackEnd(self)

    # self.block = True  # Note: qt emits a signal if a widget is populated. Thus one has to block the event after populating

  def __makeClassTree(self, objTree):
    widget = self.ui.treeClass
    widget.clear()
    root_id = 0
    root_tag = objTree["nodes"][0]

    rootItem = QTreeWidgetItem(widget)
    widget.setColumnCount(1)
    # rootItem.root = root
    rootItem.setText(0, root_tag)
    # no_id = objTree["IDs"][root]
    rootItem.path = objTree["tree"].getAncestors(root_id)
    # rootItem.setSelected(True)
    # rootItem.subject = None
    # rootItem.object = root
    # rootItem.predicate = None
    # rootItem.graph_ID = root
    # widget.addTopLevelItem(rootItem)
    # self.current_class = root

    makeTree(objTree, root_id, rootItem)  # , stack=[], items={root: rootItem})
    widget.show()
    widget.expandAll()
    # self.current_subclass = root
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
    self.gui_objects["selectors"]["textValue"].blockSignals(True)
    self.gui_objects["selectors"]["textValue"].clear()
    self.gui_objects["selectors"]["textValue"].setPlainText(data)
    self.gui_objects["selectors"]["textValue"].blockSignals(False)

  def __populateClassSubclassElucidation(self, data):
    self.gui_objects["selectors"]["textValue"].blockSignals(True)
    self.gui_objects["selectors"]["textValue"].clear()
    self.gui_objects["selectors"]["textValue"].setPlainText(data)
    self.gui_objects["selectors"]["textValue"].blockSignals(False)

  def __populateInteger(self, data):
    value = data["value"]
    self.gui_objects["selectors"]["integer"].blockSignals(True)
    self.gui_objects["selectors"]["integer"].clear()
    self.gui_objects["selectors"]["integer"].setValue(value)
    self.gui_objects["selectors"]["integer"].blockSignals(False)
    pass

  def __editIdentifier(self, data):
    text = data["text"]
    self.gui_objects["selectors"]["string"].clear()
    self.gui_objects["selectors"]["string"].setText(text)

  def __showInteger(self):
    self.gui_objects["selectors"]["integer"].show()
    self.gui_objects["groups"]["classList"].show()

  def __hideInteger(self):
    self.gui_objects["selectors"]["integer"].hide()
    self.gui_objects["groups"]["classList"].hide()

  def __makePath(self, item):
    texts = []
    while item is not None:
      texts.append(item.text(0))
      item = item.parent()
    texts.reverse()
    path = DELIMITERS["path"].join(texts)
    # print(">>>>>>>>>>>>>>>>>>>>front end -- path", path)
    return path

  def dialogYesNo(self, message="hi", buttons=["NO", "YES"]):

    return makeMessageBox(message=message, buttons=buttons)

  def stringDialog(self, state, Event, prompt, placeholder_text, limiting_list, on_fail):

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
      message = {"file_name": name}
      self.backEnd.processEvent(state, Event, message)
    elif on_fail != "close":
      print(">>> I do not know what to do")
    else:
      self.close()

  def controls(self, gui_class, gui_obj, action, *contents):
    """
    receives messages from backend except
    - string dialog
    - file-name dialog
    """
    # if gui_obj == "string":
    #   print("debugging -- controls", gui_class, gui_obj, action, *contents)
    self.gui_objects_controls[gui_class][gui_obj][action](*contents)

  def on_pushCreate_pressed(self):
    self.backEnd.processEvent("initialised", "create", None)

  def on_pushLoad_pressed(self):
    self.backEnd.processEvent("load")

  def on_listClasses_itemClicked(self, item):
    """
    generates a message
    - class_ID
    - path within class to chosen tree item
    """
    # if self.block:
    #   self.block = False
    #   return

    class_ID = item.text()
    # print("debugging -- ", class_ID)
    listTree_item = self.ui.treeClass.currentItem()
    path = self.__makePath(listTree_item)
    message = {"class": class_ID,
               "path" : path}
    self.backEnd.processEvent("class_list_clicked", "selected", message)

  def on_treeClass_itemPressed(self, item, column):
    """
    generates a message
    - class_ID === graph_ID
    - triple associated with the chosen tree item
    - path within class to chosen tree item
    """

    self.current_tree_item = item
    # graph_ID, object, predicate, subject = self.__getItemInfo(item)
    # self.path = self.__makePath(item)  # used in instantiation
    # self.triple = (subject, predicate, object)
    # print("FrontEnd -- debugging selected item:", subject, predicate, object)
    self.reversed_path = item.reversed_path
    message = {"reversed_path": self.reversed_path,
               "node_tag"         : item.text(0),
               "node_ID" : item.node_id}
    self.backEnd.processEvent("show_tree", "selected", message)

  def __getItemInfo(self, item):
    self.triple = (item.subject, item.predicate, item.object)
    subject = item.subject
    object = item.object
    predicate = item.predicate
    graph_ID = item.graph_ID
    return graph_ID, object, predicate, subject

  @pyqtSlot(int)
  def on_spinNumber_valueChanged(self, number):
    pass

  def on_pushAcceptInteger_pressed(self):
    number = self.ui.spinNumber.value()
    item = self.ui.treeClass.currentItem()
    message = {"reversed_path"   : self.reversed_path,
               "node_tag" : item.text(0),
               "node_ID"  : item.node_id,
               "integer": number}
    self.backEnd.processEvent("wait_for_ID", "got_integer", message)
    pass

  def on_editString_returnPressed(self):
    pass

  def on_pushAcceptString_pressed(self):
    string = self.ui.editString.text()
    message = {"triple": self.triple,
               "reversed_path"  : self.reversed_path,
               "string": string}
    self.backEnd.processEvent("wait_for_ID", "got_string", message)
    pass

  def on_pushInstantiate_pressed(self):
    """
    generates a message
    - triple associated with the chosen tree item
    - path within class to chosen tree item
    """
    message = {"triple": self.triple,
               "path"  : self.path}
    self.backEnd.processEvent("wait_for_ID", "add_new_ID", message)

  def on_pushVisualise_pressed(self):
    self.backEnd.processEvent("visualise", "dot_plot", {})


if __name__ == "__main__":
  import sys

  app = QApplication(sys.argv)

  icon_f = "task_ontology_foundation.svg"
  icon = os.path.join(os.path.abspath("resources/icons"), icon_f)
  app.setWindowIcon(QtGui.QIcon(icon))

  MainWindow = PeriContoPyQtFrontEnd()
  MainWindow.show()
sys.exit(app.exec_())
