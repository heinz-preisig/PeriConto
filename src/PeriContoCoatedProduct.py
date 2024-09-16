#!/usr/local/bin/python3

"""
This version uses RDF syntax for the predicates. The subjects and objects are Literals. The latter caused problems
when saving using the serializers. It can be saved but not read afterwards.

So the approach is to use an internal representation of the predicates and translate when loading and saving.


"""

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


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
from PeriConto import saveWithBackup, COLOURS, EDGE_COLOUR, QBRUSHES
# from graphHAP import Graph
from PeriContoCoatedProduct_gui import Ui_MainWindow
from resources.pop_up_message_box import makeMessageBox
from resources.resources_icons import roundButton
from resources.single_list_selector_impl import SingleListSelector
from resources.ui_string_dialog_impl import UI_String


def getPath(truples, origin, destination, thepath, visited):  # "start"):
  """
  we search backwards from the destination to the origin
  truples is a weird thing: subject, object, predicate
  it really is a tuple of subject, object with the predicate added for further use.
  """
  # if visited == "start":
  #   thepath = []
  #   visited = []

  if origin not in visited:
    visited.append(origin)
    match = matchTriples(truples, origin, None, None)
    for s, o, p in match:
      thepath.append(s)
      if o == destination:
        thepath.append(o)
        return thepath
      else:
        getPath(truples, o, destination, thepath, visited)

  return thepath


def matchTriples(truples, subject=None, predicate=None, object=None):
  # res = []
  # for t in truples:
  #   a = (not subject or t[0] == subject)
  #   b = (not predicate or t[2] == predicate)
  #   c = (not object or t[1] == object)
  #   print(">> ", a,b,c,subject, predicate, object, t)
  #   if a and b and c:
  #     res.append(t)

  r = [t for t in truples if (
          (not subject or t[0] == subject)
          and (not predicate or t[2] == predicate)
          and (not object or t[1] == object))]
  return r


class CoatedProduct(QMainWindow):
  def __init__(self):
    super(CoatedProduct, self).__init__()

    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    roundButton(self.ui.pushLoad, "load", tooltip="load ontology")
    roundButton(self.ui.pushCreate, "plus", tooltip="create")
    roundButton(self.ui.pushVisualise, "dot_graph", tooltip="visualise ontology")
    roundButton(self.ui.pushSave, "save", tooltip="save ontology")
    roundButton(self.ui.pushExit, "exit", tooltip="exit")

    self.gui_objects = {
            "load"                      : self.ui.pushLoad,
            "create"                    : self.ui.pushCreate,
            "visualise"                 : self.ui.pushVisualise,
            "save"                      : self.ui.pushSave,
            "exit"                      : self.ui.pushExit,
            "ClassSubclassElucidation"  : self.ui.groupClassSubclassElucidation,
            "ValueElucidation"          : self.ui.groupValueElucidation,
            "AddValueElucidation_button": self.ui.pushAcceptValueElucidation,#pushAddValueElucidation,
            "PrimitiveString"           : self.ui.groupString,
            "integer"         : self.ui.groupQuantityMeasure,
            }
    self.gui_objects_clear = {
            "text_eluciation": self.ui.textValueElucidation,
            "identifier"     : self.ui.editString,
            }
    w = 150
    h = 25
    # for i in ["add_subclass", "add_primitive", "link_new_class", "link_existing_class"]:
    #   self.gui_objects[i].setFixedSize(w, h)

    self.ontology_graph = None
    self.ontology_root = None
    self.changed = False

    self.__ui_state("start")
    self.current_class = None
    self.current_subclass = None
    self.current_item_text_ID = None
    self.subclass_names = {}
    self.primitives = {}
    self.class_names = []
    self.class_path = []
    self.path = []
    self.link_lists = {}
    self.class_definition_sequence = []
    self.TTLfile = None
    self.elucidations = {}
    self.selected_item = None
    self.root_class = None
    self.load_elucidation = False
    self.done = False
    self.transition_points = {}  # keeps the information on where the transition to another class was made
    self.complete_path = []
    self.local_path = None
    self.database = {}

  def __ui_state(self, state):
    # what to show
    if state == "start":
      show = ["load",
              "create",
              "exit",
              ]
    elif state == "show_tree":
      show = ["save",
              "exit",
              "visualise",
              ]
    elif state == "selected_subclass":
      show = ["save",
              "exit",
              "ClassSubclassElucidation",
              ]
    elif state == "selected_class":
      show = ["save",
              "exit",
              "ClassSubclassElucidation",
              ]
    elif state == "selected_integer":
      show = ["save",
              "exit",
              "ValueElucidation",
              "integer",
              ""
              ]
    elif state == "selected_string":
      show = ["save",
              "exit",
              "ValueElucidation",
              "PrimitiveString",
              ]
    elif state == "selected_value":
      show = ["save",
              "exit",
              "ValueElucidation",
              ]
    else:
      show = []
      print("ooops -- no such state", state)

    for b in self.gui_objects:
      if b not in show:
        self.gui_objects[b].hide()
      else:
        self.gui_objects[b].show()

    if state != "start":
      for w in self.gui_objects_clear:
        self.gui_objects_clear[w].clear()

  def __createTree(self, origin):
    widget = self.ui.treeClass
    widget.clear()

    rootItem = QTreeWidgetItem(widget)
    widget.setColumnCount(1)
    rootItem.root = origin
    rootItem.setText(0, origin)
    rootItem.setSelected(True)
    rootItem.predicate = None
    widget.addTopLevelItem(rootItem)
    self.current_class = origin
    truples = self.__prepareTree(origin)
    self.__makeTree(truples, origin=origin, stack=[], items={origin: rootItem})
    # self.__makeTree(origin=Literal(origin), subject_stack=[], parent=rootItem)
    widget.show()
    widget.expandAll()
    self.current_subclass = origin
    self.__ui_state("show_tree")

  def __prepareTree(self, origin):
    graph = self.CLASSES[self.current_class]
    # print(graph.serialize(format='turtle'))
    # print("debugging", origin)
    truples = []
    for subject, predicate, object_ in graph.triples((None, None, None)):
      s = str(subject)
      p = MYTerms[predicate]
      o = str(object_)
      if p not in ["value"] + PRIMITIVES:
        truples.append((s, o, p))
      else:
        truples.append((o, s, p))
    return truples

  def __makeTree(self, truples, origin=[], stack=[], items={}):
    for s, o, p in truples:
      if (s, o, p) not in stack:
        if s != origin:
          if o in items:
            # print("add %s <-- %s" % (o, s),p)
            item = QTreeWidgetItem(items[o])
            # print("debugging -- color",p )
            # item.setBackground(0, COLOURS[p])
            item.predicate = p
            item.setForeground(0, QBRUSHES[p])
            stack.append((s, o, p))
            item.setText(0, s)
            items[s] = item
            self.__makeTree(truples, origin=s, stack=stack, items=items)

  def on_pushCreate_pressed(self):
    dialog = UI_String("name for your ontology file", placeholdertext="file name extension is default")
    dialog.exec_()
    name = dialog.getText()
    if name:
      fname = name.split(".")[0] + ".json"
      self.JsonFile = os.path.join(ONTOLOGY_DIRECTORY, fname)
    else:
      self.close()

    dialog = UI_String("root identifier", placeholdertext="provide an identifier for the root")
    dialog.exec_()
    name = dialog.getText()
    if not name:
      self.close()
    else:
      self.root_class = name

    self.CLASSES = {self.root_class: Graph('Memory', Literal(self.root_class))}
    self.current_class = self.root_class
    self.subclass_names[self.root_class] = [self.root_class]
    self.class_names.append(self.root_class)
    self.class_path = [self.root_class]
    self.link_lists[self.root_class] = []
    self.ui.listClasses.addItems(self.class_path)
    self.class_definition_sequence.append(self.root_class)
    self.primitives[self.root_class] = {self.root_class: []}
    self.changed = True

    self.__createTree(self.root_class)

  def on_treeClass_itemPressed(self, item, column):
    #   self.done = False
    #   self.on_treeClass_itemSelectionChanged()
    #
    # def on_treeClass_itemSelectionChanged(self):
    #   if self.done:
    #     self.done = False
    #     return
    #
    #   self.done = True
    item_list = self.ui.treeClass.selectedItems()
    # print("debugging", item_list.__class__, len(item_list))
    if len(item_list) == 1:
      item = item_list[0]
    else:
      return
    column = 0
    text_ID = item.text(column)
    self.current_item_text_ID = text_ID
    try:
      predicate = item.predicate
    except:
      item.predicate = None
      predicate = None
    # print("debugging -- ", text_ID)
    self.selected_item = item

    graph = self.CLASSES[self.current_class]
    origin = text_ID
    destination = self.current_class
    truples = self.__prepareTree(self.current_class)
    self.local_path = getPath(truples, origin, destination, [], [])
    print("debugging -- local path:", self.local_path)

    # if text_ID in self.class_names:
    if self.__isClass(text_ID):
      print("debugging -- is class", text_ID)
      self.__ui_state("selected_class")
      if self.current_class != text_ID:
        self.transition_points[self.current_class] = self.local_path
        self.__shiftClass(text_ID)
    elif self.__islinked(text_ID):
      print("debugging -- is linked", text_ID)
      self.__ui_state("selected_subclass")
      # self.__pathToSubclass(text_ID)
    elif self.__isSubClass(text_ID):
      print("debugging -- it is a subclass", text_ID)
      self.__ui_state("selected_subclass")
      # self.__pathToSubclass(text_ID)
      self.current_subclass = text_ID
    elif self.__isValue(predicate):
      self.__ui_state("selected_value")
      self.complete_path = self.__makeCompletePath()
      print("debugging -- complete path", self.complete_path)
    elif text_ID == "integer":
      print("debugging -- is a integer")
      self.__ui_state("selected_integer")
    elif text_ID == "string":
      print("debugging -- is a string")
      self.__ui_state("selected_string")
    elif text_ID == "comment":
      self.__ui_state("selected_comment")
    else:
      print("should not come here")

    if self.__hasElucidation(text_ID, predicate):
      self.load_elucidation = True
      p = self.__makePathName(text_ID)
      not_exist = None
      try:
        self.ui.textClassSubclassElucidation.setPlainText(self.elucidations[p])
      except:
        not_exist = p
        self.ui.textClassSubclassElucidation.clear()

      if not_exist:
        self.elucidations[not_exist] = ""

  # def on_treeClass_itemSelectionChanged(self):
  #   print("debugging -- selection changed")

  # def on_treeClass_itemDoubleClicked(self, item, column):
  #   print("debugging -- double click", item.text(0))
  #   ID = str(item.text(column))
  #   if self.__isSubClass(ID):
  #     # rename subclass
  #     dialog = UI_String("new name", placeholdertext=str(item.text(0)))
  #     dialog.exec_()
  #     new_name = dialog.getText()
  #     if new_name:
  #       graph = self.CLASSES[self.current_class]
  #       for s, p, o in graph.triples((None, None, Literal(ID))):
  #         print("debugging -- change triple", s, p, o)
  #         self.CLASSES[self.current_class].remove((s, p, o))
  #         object = makeRDFCompatible(new_name)
  #         self.CLASSES[self.current_class].add((s, RDFSTerms["is_a_subclass_of"], object))
  #
  #       for s, p, o in graph.triples((Literal(ID), None, None)):
  #         print("debugging -- change triple", s, p, o)  # add to graph
  #         self.CLASSES[self.current_class].remove((s, p, o))
  #         subject = makeRDFCompatible(new_name)
  #         self.CLASSES[self.current_class].add((subject, RDFSTerms["is_a_subclass_of"], o))
  #
  #       self.__createTree(self.current_class)

  def on_textValueElucidation_textChanged(self):
    # print("debugging change text")
    if self.load_elucidation:
      self.load_elucidation = False
      self.ui.pushAcceptValueElucidation.hide()
      return

    self.ui.pushAcceptValueElucidation.show()

  # def on_pushAddValueElucidation_pressed(self):
  #   self.load_elucidation = True
  #   self.ui.pushAddValueElucidation.hide()
  #   d = self.ui.textValueElucidation.toPlainText()
  #   self.complete_path = self.__makeCompletePath()
  #   print("debugging -- ", self.complete_path, d)
  #   path = self.complete_path.pop(0)
  #   modified_path = ["comment"]
  #   [modified_path.append(i) for i in self.complete_path]
  #   self.database[str(modified_path)] = d
  #
  #   pass

  def __makePathName(self, text_ID):
    p = self.root_class
    for i in self.class_path[1:]:
      p = p + ".%s" % i
    if text_ID not in p:
      item_name = text_ID
      p = p + ".%s" % item_name
    return p

  def __makeCompletePath(self):
    complete_path = []
    for e in self.class_path[:-1]:
      complete_path += self.transition_points[e]
    complete_path += self.local_path
    return complete_path

  def __isClass(self, ID):
    return ID in self.class_names

  def __isSubClass(self, ID):
    return ID in self.subclass_names[self.current_class]

  def __isPrimitive(self, text_ID):
    print("debugging -- is primitive", text_ID)
    return text_ID in PRIMITIVES

  def __isValue(self, predicate):
    return predicate == VALUE

  def __islinked(self, ID):
    for cl in self.link_lists:
      for linked_class, linked_to_class, linked_to_subclass in self.link_lists[cl]:
        if linked_to_class == self.current_class:
          if linked_to_subclass == ID:
            return True

    return False

  def __hasElucidation(self, text_ID, predicate):
    return self.__isClass(text_ID) or self.__isSubClass(text_ID) or self.__isValue(predicate)

  # def on_pushAddSubclass_pressed(self):
  #   print("debugging -- add subclass")
  #
  #   # get an identifier for the subclass
  #   forbidden = sorted(self.subclass_names[self.current_class]) + sorted(self.class_names)
  #   dialog = UI_String("name for subclass", limiting_list=forbidden)
  #   dialog.exec_()
  #   subclass_ID = dialog.getText()
  #
  #   if not subclass_ID:
  #     return
  #
  #   # keep track of names
  #   self.subclass_names[self.current_class].append(subclass_ID)
  #   self.primitives[self.current_class][self.current_subclass] = []
  #
  #   # elucidation
  #   p = self.__makePathName(subclass_ID)
  #   self.elucidations[p] = None
  #   self.ui.textElucidation.clear()
  #
  #   # add to graph
  #   subject = makeRDFCompatible(subclass_ID)
  #   object = makeRDFCompatible(self.current_subclass)
  #   predicate = "is_a_subclass_of"
  #   self.CLASSES[self.current_class].add((subject, RDFSTerms["is_a_subclass_of"], object))
  #
  #   # generate GUI tree
  #   self.__createTree(self.current_class)
  #   # parent_item = self.ui.treeClass.currentItem()
  #   # item = QTreeWidgetItem(parent_item)
  #   # item.predicate = predicate
  #   # item.setText(0, subclass_ID)
  #   # self.ui.treeClass.expandAll()
  #   self.changed = True

  # def on_pushAddPrimitive_pressed(self):
  #   # print("debugging -- add primitive")
  #   forbidden = self.subclass_names[self.current_class]  # TODO: no second linked primitive allowed
  #   dialog = UI_String("name for primitive", limiting_list=forbidden)
  #   dialog.exec_()
  #   primitive_ID = dialog.getText()
  #   if not primitive_ID:
  #     return
  #
  #   permitted_classes = PRIMITIVES
  #   dialog = SingleListSelector(permitted_classes)
  #   dialog.exec_()
  #   primitive_class = dialog.getSelection()
  #   # print("debugging")
  #   if not primitive_class:
  #     return
  #
  #   # add to graph
  #   item = self.__addItemToTree(primitive_ID, "value", self.current_subclass)
  #   self.__addItemToTree(primitive_class, primitive_class, primitive_ID, parent_item=item)
  #   if self.current_subclass not in self.primitives[self.current_class]:
  #     self.primitives[self.current_class][self.current_subclass] = []
  #   self.primitives[self.current_class][self.current_subclass].append(primitive_ID)

  # def __addItemToTree(self, internal_object, predicate, internal_subject, parent_item=None):
  #   object = makeRDFCompatible(internal_object)
  #   subject = makeRDFCompatible(internal_subject)
  #   self.CLASSES[self.current_class].add((subject, RDFSTerms[predicate], object))
  #   # generate GUI tree
  #   if not parent_item:
  #     parent_item = self.ui.treeClass.currentItem()
  #   item = QTreeWidgetItem(parent_item)
  #   item.setText(0, internal_object)
  #   item.setBackground(0, PRIMITIVE_COLOUR)
  #   self.ui.treeClass.expandAll()
  #   self.changed = True
  #   return item

  # def on_pushAddNewClass_pressed(self):
  #   # print("debugging -- add class")
  #
  #   forbidden = sorted(self.class_names)
  #   dialog = UI_String("name for subclass", limiting_list=forbidden)
  #   dialog.exec_()
  #   class_ID = dialog.getText()
  #   if not class_ID:
  #     return
  #
  #   self.CLASSES[class_ID] = Graph('Memory', Literal(class_ID))
  #   self.class_definition_sequence.append(class_ID)
  #   self.subclass_names[class_ID] = []
  #   self.primitives[class_ID] = {class_ID: []}
  #
  #   # elucidation
  #   self.ui.textElucidation.clear()
  #   self.elucidations[class_ID] = None
  #
  #   # make link
  #   subject = makeRDFCompatible(class_ID)
  #   object = makeRDFCompatible(self.current_subclass)
  #   self.CLASSES[self.current_class].add((subject, RDFSTerms["link_to_class"], object))
  #
  #   if class_ID not in self.link_lists:
  #     self.link_lists[class_ID] = []
  #   self.link_lists[class_ID].append((class_ID, self.current_class, self.current_subclass))
  #
  #   self.__createTree(class_ID)
  #   self.class_names.append(class_ID)
  #   self.__addToClassPath(addclass=class_ID)
  #   self.current_class = class_ID
  #   self.class_definition_sequence.append(class_ID)
  #   self.primitives[class_ID] = {"root": []}
  #   self.changed = True

  # def on_pushAddExistingClass_pressed(self):
  #   # print("debugging -- pushExistingClass")
  #   permitted_classes = self.__permittedClasses()
  #
  #   # print("debugging -- ", permitted_classes)
  #   if permitted_classes:
  #     dialog = SingleListSelector(permitted_classes)
  #     dialog.exec_()
  #     selection = dialog.getSelection()
  #     # print("debugging")
  #     if not selection:
  #       return
  #
  #     class_ID = selection
  #     subject = makeRDFCompatible(class_ID)
  #     object = makeRDFCompatible(self.current_subclass)
  #     self.CLASSES[self.current_class].add((subject, RDFSTerms["link_to_class"], object))
  #
  #     if class_ID not in self.link_lists:
  #       self.link_lists[class_ID] = []
  #     self.link_lists[class_ID].append((class_ID, self.current_class, self.current_subclass))
  #
  #     parent_item = self.ui.treeClass.currentItem()
  #     item = QTreeWidgetItem(parent_item)
  #     item.setText(0, class_ID)
  #     columns = item.columnCount()
  #     item.setBackground(0, LINK_COLOUR)
  #     self.ui.treeClass.expandAll()
  #     self.changed = True

  def on_editString_returnPressed(self):
    s = self.ui.editString.text()
    ss = str(s)
    print("not yet installed textString", ss)
    self.complete_path = self.__makeCompletePath()
    print("debugging -- ", self.complete_path)
    self.database[str(self.complete_path)] = ss

  def on_spinNumber_valueChanged(self, d):
    print("net yet installed spinNumber", d)
    self.complete_path = self.__makeCompletePath()
    print("debugging -- ", self.complete_path)
    self.database[str(self.complete_path)] = d

  def __permittedClasses(self):
    permitted_classes = []
    for cl in self.CLASSES:
      if cl != self.current_class:
        if cl not in self.link_lists[cl]:
          if cl not in self.class_path:
            permitted_classes.append(cl)
    return permitted_classes

  # def __pathToSubclass(self, text_ID):
  #
  #   if text_ID not in self.path:
  #     self.path.append(text_ID)
  #   else:
  #     i = self.class_path.index(text_ID)
  #     self.class_path = self.class_path[:i + 1]
  #
  #   self.ui.listClasses.clear()
  #   self.ui.listClasses.addItems(self.path)

  def __addToClassPath(self, addclass):
    self.class_path.append(addclass)
    self.ui.listClasses.clear()
    self.ui.listClasses.addItems(self.class_path)

  # def __addToPath(self, addnode):
  #   self.class_path.append(addnode)
  #   self.path.append(addnode)
  #   self.ui.listClasses.clear()
  #   self.ui.listClasses.addItems(self.path)

  #
  def __cutClassPath(self, cutclass):
    i = self.class_path.index(cutclass)
    self.class_path = self.class_path[:i + 1]
    self.ui.listClasses.clear()
    self.ui.listClasses.addItems(self.class_path)

  # def __cutPath(self, cutclass):
  #   i = self.class_path.index(cutclass)
  #   self.class_path = self.class_path[:i + 1]
  #   self.ui.listClasses.clear()
  #   self.ui.listClasses.addItems(self.class_path)

  def on_listClasses_itemClicked(self, item):
    class_ID = item.text()
    # print("debugging -- ", class_ID)
    self.__shiftClass(class_ID)

  def __shiftClass(self, class_ID):
    # print("debugging ---------------")
    self.current_class = class_ID
    self.__createTree(class_ID)
    if class_ID not in self.class_path:
      self.__addToClassPath(class_ID)
    else:
      self.__cutClassPath(class_ID)
    #   self.__addToPath(class_ID)
    # else:
    #   self.__cutPath(class_ID)

  def on_pushExit_pressed(self):
    self.closeMe()

  def closeEvent(self, event):
    self.closeMe()

  def closeMe(self):
    if self.changed:
      dialog = makeMessageBox(message="save changes", buttons=["YES", "NO"])
      if dialog == "YES":
        # print("save")
        self.on_pushSave_pressed()

      elif dialog == "NO":
        pass
        # print("exit")

    else:
      pass
      # print("no changes")
    self.close()

  def on_pushSave_pressed(self):
    # print("debugging -- pushSave")

    # NOTE: this does work fine, but one cannot read it afterwards. Issue is the parser. It assumes that the subject and
    # NOTE: object are in the namespace.

    # conjunctiveGraph = ConjunctiveGraph('Memory')
    # for cl in self.class_definition_sequence:
    #   uri = Literal(cl)
    #   for s,p,o in self.CLASSES[cl].triples((None,None,None)):
    #     print(s,p,o)
    #     conjunctiveGraph.get_context(uri).add([s,p,o])
    #
    # print("debugging")
    #
    # f = self.JsonFile.split(".")[0] + ".nqd"
    # inf = open(f,'w')
    # inf.write(conjunctiveGraph.serialize(format="nquads"))
    # inf.close()
    #
    # print("written to file ", f)

    # Note: saving it with the RDF syntax did not work for loading. Needs more reading...?

    data = {}
    graphs = {}
    for cl in self.class_definition_sequence:
      graphs[cl] = []
      for s, p, o in self.CLASSES[cl].triples((None, None, None)):
        my_p = MYTerms[p]
        graphs[cl].append((s, my_p, o))

    data["root"] = self.root_class
    data["graphs"] = graphs
    data["elucidations"] = self.elucidations
    data["database"] = self.database

    saveWithBackup(data, self.JsonFile)

    dot = self.__makeDotGraph()

    # graphs = Graph("Memory")
    # for cl in self.class_definition_sequence:
    #   # graphs[cl] = []
    #   for t in self.CLASSES[cl].triples((None, None, None)):
    #     graphs.add(t)
    #
    # self.JsonFile = self.JsonFile.split(".ttl")[0] + ".nquads"
    #
    # graphs.serialize(TTLFile, format="nquads")
    # saveWithBackup(graphs, TTLFile)
    # self.changed = False

    self.changed = False

  def on_pushLoad_pressed(self):
    dialog = QFileDialog.getOpenFileName(None,
                                         "Load Ontology",
                                         ONTOLOGY_DIRECTORY,
                                         "*.json",
                                         )
    self.JsonFile = dialog[0]
    if dialog[0] == "":
      print("not file specified --> closing")
      self.close()
      return

    # print("debugging")
    data = getData(self.JsonFile)
    self.root_class = data["root"]
    self.elucidations = data["elucidations"]

    graphs = data["graphs"]
    self.CLASSES = {}
    for g in graphs:
      self.class_definition_sequence.append(g)
      self.class_names.append(g)
      self.subclass_names[g] = []
      self.primitives[g] = {g: []}
      self.link_lists[g] = []
      self.CLASSES[g] = Graph()
      for s, p_internal, o in graphs[g]:
        subject = makeRDFCompatible(s)
        object = makeRDFCompatible(o)
        p = RDFSTerms[p_internal]
        self.CLASSES[g].add((subject, p, object))
        # print("debugging -- graph added", g,s,p,o)
        if p == RDFSTerms["is_a_subclass_of"]:
          self.subclass_names[g].append(s)
        elif p == RDFSTerms["link_to_class"]:
          if g not in self.link_lists:
            self.link_lists[g] = []
          self.link_lists[g].append((s, g, o))
        elif p == RDFSTerms["value"]:
          if g not in self.primitives:
            self.primitives[g] = {}
          if o not in self.primitives[g]:
            self.primitives[g][o] = [s]
          else:
            self.primitives[g][o].append(s)
        elif p_internal in PRIMITIVES:
          if g not in self.primitives:
            self.primitives[g] = {}
          if o not in self.primitives[g]:
            self.primitives[g][o] = [s]
          else:
            self.primitives[g][o].append(s)
        else:
          if o not in self.primitives[g]:
            self.primitives[g][o] = [s]
          else:
            self.primitives[g][o].append(s)

    self.current_class = self.root_class
    self.class_path = [self.root_class]
    self.__createTree(self.root_class)
    self.ui.listClasses.addItems(self.class_path)
    self.__ui_state("show_tree")

    # ====================================
    # graph = self.CLASSES[self.current_class]
    # gugus = getpath(graph, "dye", self.root_class, [])
    # print(gugus)
    # pass

  def on_pushVisualise_pressed(self):

    dot = self.__makeDotGraph()
    dot.view()

  def __makeDotGraph(self):
    graph_overall = Graph()
    for cl in self.CLASSES:
      for t in self.CLASSES[cl].triples((None, None, None)):
        graph_overall.add(t)
    dot = plot(graph_overall, self.class_names)
    # print("debugging -- dot")
    graph_name = self.root_class
    dot.render(graph_name, directory=ONTOLOGY_DIRECTORY)
    return dot


if __name__ == "__main__":
  import sys

  app = QApplication(sys.argv)

  icon_f = "task_ontology_foundation.svg"
  icon = os.path.join(os.path.abspath("resources/icons"), icon_f)
  app.setWindowIcon(QtGui.QIcon(icon))

  MainWindow = CoatedProduct()
  MainWindow.show()
  sys.exit(app.exec_())
