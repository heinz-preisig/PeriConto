#!/usr/local/bin/python3

"""
This version uses RDF syntax for the predicates. The subjects and objects are Literals. The latter caused problems
when saving using the serializers. It can be saved but not read afterwards.

So the approach is to use an internal representation of the predicates and translate when loading and saving.


"""

#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


import json
import os

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from graphviz import Digraph
from rdflib import Graph
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD

# from graphHAP import Graph
from ontologybuilderHAP_gui import Ui_MainWindow
from resources.pop_up_message_box import makeMessageBox
from resources.resources_icons import roundButton
from resources.single_list_selector_impl import SingleListSelector
from resources.ui_string_dialog_impl import UI_String

# from rdflib import Graph, ConjunctiveGraph, RDF, BNode, Literal, RDFS, Dataset
# from rdflib.plugins.stores.memory import Memory

# self.root_class = "coating"
# self.root_class = "coatedProduct"

RDFSTerms = {
        "is_a_subclass_of": RDFS.subClassOf,
        "link_to_class"   : RDFS.isDefinedBy,
        "value"           : RDF.value,
        "comment"         : RDFS.comment,
        "integer"         : XSD.integer,
        "string"          : XSD.string,
        }

MYTerms = {v: k for k, v in RDFSTerms.items()}

PRIMITIVES = ["integer", "string", "comment"]
ADD_ELUCIDATIONS = ["class", "subclass", "value"]

ENDPOINTS = ["link_to_class", "value"]  # , "integer", "string"]

COLOURS = {
        "is_a_subclass_of": QtGui.QColor(255, 255, 255, 255),
        "link_to_class"   : QtGui.QColor(255, 100, 5, 255),
        "value"           : QtGui.QColor(155, 155, 255),
        "comment"         : QtGui.QColor(155, 155, 255),
        "integer"         : QtGui.QColor(155, 155, 255),
        "string"          : QtGui.QColor(255, 200, 200, 255),
        }

DIRECTION = {
        "is_a_subclass_of": 1,
        "link_to_class"   : 1,
        "value"           : -1,
        "comment"         :-1,
        "integer"         : -1,
        "string"          : -1,
        }

LINK_COLOUR = QtGui.QColor(255, 100, 5, 255)
PRIMITIVE_COLOUR = QtGui.QColor(255, 3, 23, 255)

TTLFile = os.path.join("../coatingOntology_HAP", "%s.json" % "HAP")
TTLDirectory = "../coatingOntology_HAP"


def plot(graph, class_names=[]):
  """
  Create Digraph plot
  """
  dot = Digraph()
  # Add nodes 1 and 2
  for s, p, o in graph.triples((None, None, None)):
    ss = str(s)
    sp = str(p)
    so = str(o)
    if ss in class_names:
      dot.node(ss, color='red', shape="rectangle")
    elif so in PRIMITIVES:
      dot.node(so, color='green', shape="rectangle")
    else:
      dot.node(ss)

    if so in class_names:
      dot.node(so, color='red', shape="rectangle")
    else:
      dot.node(so)

    my_p = MYTerms[p]
    if DIRECTION[my_p] == 1:
      dot.edge(ss, so, label=my_p, color="blue")
    else:
      dot.edge(so, ss, label=my_p, color = "green" )
    # if my_p in PRIMITIVES+ENDPOINTS:
    #   dot.edge(so,ss,label=my_p)
    # else:
    #   dot.edge(ss, so, label=my_p)

  # Visualize the graph
  return dot


def putData(data, file_spec, indent="  "):
  print("writing to file: ", file_spec)
  dump = json.dumps(data, indent=indent)
  with open(file_spec, "w+") as f:
    f.write(dump)


def getFilesAndVersions(abs_name, ext):
  base_name = os.path.basename(abs_name)
  ver = 0  # initial last version
  _s = []
  directory = os.path.dirname(abs_name)  # listdir(os.getcwd())
  files = os.listdir(directory)

  for f in files:
    n, e = os.path.splitext(f)
    #        print 'name', n
    if e == ext:  # this is another type
      if n[0:len(base_name) + 1] == base_name + "(":  # only those that start with name
        #  extract version
        l = n.index("(")
        r = n.index(")")
        assert l * r >= 0  # both must be there
        v = int(n[l + 1:r])
        ver = max([ver, v])
        _s.append(n)
  return _s, ver


def saveBackupFile(path):
  ver_temp = "(%s)"
  (abs_name, ext) = os.path.splitext(path)  # path : directory/<name>.<ext>
  if os.path.exists(path):
    _f, ver = getFilesAndVersions(abs_name, ext)
    old_path = path
    new_path = abs_name + ver_temp % str(ver + 1) + ext
    next_path = abs_name + ver_temp % str(ver + 2) + ext
    os.rename(old_path, new_path)
    return old_path, new_path, next_path
  else:
    print("Error -- no such file : %s" % path, file=sys.stderr)
    return


def saveWithBackup(data, path):
  if os.path.exists(path):
    old_path, new_path, next_path = saveBackupFile(path)
  putData(data, path)


def getData(file_spec):
  # print("get data from ", file_spec)
  if os.path.exists(file_spec):
    f = open(file_spec, "r")
    data = json.loads(f.read())
    return data
  else:
    return None


def makeRDFCompatible(identifier):
  """
  To be adapted to imported notation.
  For now it generates rdflib Literals
  """
  return Literal(identifier)


class OntobuilderUI(QMainWindow):
  def __init__(self):
    super(OntobuilderUI, self).__init__()
    self.ui = Ui_MainWindow()
    self.ui.setupUi(self)

    roundButton(self.ui.pushLoad, "load", tooltip="load ontology")
    roundButton(self.ui.pushVisualise, "dot_graph", tooltip="visualise ontology")
    roundButton(self.ui.pushCreate, "plus", tooltip="create")
    roundButton(self.ui.pushSave, "save", tooltip="save ontology")
    roundButton(self.ui.pushExit, "exit", tooltip="exit")

    self.gui_objects = {
            "load"               : self.ui.pushLoad,
            "create"             : self.ui.pushCreate,
            "visualise"          : self.ui.pushVisualise,
            "save"               : self.ui.pushSave,
            "exit"               : self.ui.pushExit,
            "add_subclass"       : self.ui.pushAddSubclass,
            "add_primitive"      : self.ui.pushAddPrimitive,
            "link_new_class"     : self.ui.pushAddNewClass,
            "link_existing_class": self.ui.pushAddExistingClass,
            "remove"             : self.ui.pushRemoveNode,
            "elucidation"        : self.ui.groupElucidation,
            "elucidation_button" : self.ui.pushAddElucidation,
            }
    w = 150
    h = 25
    for i in ["add_subclass", "add_primitive", "link_new_class", "link_existing_class"]:
      self.gui_objects[i].setFixedSize(w, h)

    self.ontology_graph = None
    self.ontology_root = None
    self.changed = False

    self.__ui_state("start")
    self.current_class = None
    self.current_subclass = None
    self.subclass_names = {}
    self.primitives = {}
    self.class_names = []
    self.class_path = []
    self.link_lists = {}
    self.class_definition_sequence = []
    self.TTLfile = TTLFile
    self.elucidations = {}
    self.selected_item = None
    self.root_class = None
    self.load_elucidation = True

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
              "add_subclass",
              "add_primitive",
              "link_new_class",
              "link_existing_class",
              "elucidation",
              ]
    elif state == "selected_class":
      show = ["save",
              "exit",
              "add_subclass",
              "add_primitive",
              "elucidation",
              ]
    elif state == "selected_primitive":
      show = ["save",
              "exit",
              ]
    elif state == "value_selected":
      show = ["save",
              "exit",
              "elucidation",
              ]
    elif state == "no_existing_classes":
      show = ["save",
              "exit",
              "add_subclass",
              "add_primitive",
              "link_new_class",
              "elucidation",
              ]
    elif state == "occupied":
      show = ["save",
              "exit",
              "elucidation",
              ]
    else:
      show = []

    for b in self.gui_objects:
      if b not in show:
        self.gui_objects[b].hide()
      else:
        self.gui_objects[b].show()

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
    tuples = self.__prepareTree(origin)
    self.__makeTree(tuples, origin=origin, stack=[], items={origin: rootItem})
    # self.__makeTree(origin=Literal(origin), subject_stack=[], parent=rootItem)
    widget.show()
    widget.expandAll()
    self.current_subclass = origin
    self.__ui_state("show_tree")

  def __prepareTree(self, origin):
    graph = self.CLASSES[self.current_class]
    # print(graph.serialize(format='turtle'))
    # print("debugging", origin)
    tuples_plus = []
    for subject, predicate, object_ in graph.triples((None, None, None)):
      s = str(subject)
      p = MYTerms[predicate]
      o = str(object_)
      if p not in ["value"] + PRIMITIVES:
        tuples_plus.append((s, o, p))
      else:
        tuples_plus.append((o, s, p))
    return tuples_plus

  def __makeTree(self, touples, origin=[], stack=[], items={}):
    for s, o, p in touples:
      if s not in stack:
        if s != origin:
          if o in items:
            # print("add %s <-- %s" % (o, s))
            item = QTreeWidgetItem(items[o])
            # print("debugging -- color",p )
            item.setBackground(0, COLOURS[p])
            item.predicate = p
            stack.append(str(s))
            item.setText(0, s)
            items[s] = item
            self.__makeTree(touples, origin=s, stack=stack, items=items)

  def on_pushCreate_pressed(self):
    dialog = UI_String("name for your ontology file", placeholdertext="file name extension is default")
    dialog.exec_()
    name = dialog.getText()
    if name:
      fname = name.split(".")[0] + ".json"
      self.TTLFile = os.path.join(TTLDirectory, fname)
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
    self.__createTree(self.root_class)
    self.current_class = self.root_class
    self.subclass_names[self.root_class] = []
    self.class_names.append(self.root_class)
    self.class_path = [self.root_class]
    self.link_lists[self.root_class] = []
    self.ui.listClasses.addItems(self.class_path)
    self.class_definition_sequence.append(self.root_class)
    self.primitives[self.root_class] = {self.root_class: []}
    self.changed = True

  def on_treeClass_itemPressed(self, item, column):
    text_ID = item.text(column)
    predicate = item.predicate
    print("debugging -- ", text_ID)
    self.selected_item = item
    # self.current_subclass = text_ID

    # if text_ID in self.class_names:
    if self.__isClass(text_ID):
      print("debugging -- is class", text_ID)
      self.__ui_state("selected_class")
      if self.current_class != text_ID:
        self.__shiftClass(text_ID)
    elif self.__islinked(text_ID):
      print("debugging -- is linked", text_ID)
      self.__ui_state("occupied")
    elif self.__isSubClass(text_ID):
      print("debugging -- it is a subclass", text_ID)
      self.__ui_state("selected_subclass")
      if not self.__permittedClasses():
        print(">> no_existing_classes")
        self.__ui_state("no_existing_classes")
      else:
        print(">>>>selected_subclass")
        self.__ui_state("selected_subclass")
      self.current_subclass = text_ID
    elif self.__isPrimitive(predicate):
      print("debugging -- is a primitive")
      self.__ui_state("selected_primitive")
    elif self.__isValue:
      self.__ui_state("value_selected")
    else:
      print("should not come here")

    if  self.__hasElucidation(text_ID, predicate):
      self.ui.pushAddElucidation.hide()
      self.load_elucidation = True
      p = self.__makePathName(text_ID)
      not_exist = None
      try:
        self.ui.textElucidation.setPlainText(self.elucidations[p])
      except:
        not_exist = p
        self.ui.textElucidation.clear()

      if not_exist:
        self.elucidations[not_exist] = ""

  def on_treeClass_itemDoubleClicked(self, item, column):
    print("debugging -- double click", item.text(0))
    ID = str(item.text(column))
    if self.__isSubClass(ID):
      # rename subclass
      dialog = UI_String("new name", placeholdertext=str(item.text(0)))
      dialog.exec_()
      new_name = dialog.getText()
      if new_name:
        graph = self.CLASSES[self.current_class]
        for s, p, o in graph.triples((None, None, Literal(ID))):
          print("debugging -- change triple", s, p, o)
          self.CLASSES[self.current_class].remove((s, p, o))
          object = makeRDFCompatible(new_name)
          self.CLASSES[self.current_class].add((s, RDFSTerms["is_a_subclass_of"], object))

        for s, p, o in graph.triples((Literal(ID), None, None)):
          print("debugging -- change triple", s, p, o)  # add to graph
          self.CLASSES[self.current_class].remove((s, p, o))
          subject = makeRDFCompatible(new_name)
          self.CLASSES[self.current_class].add((subject, RDFSTerms["is_a_subclass_of"], o))

        self.__createTree(self.current_class)

  def on_textElucidation_textChanged(self):
    # print("debugging change text")
    if self.load_elucidation:
      self.load_elucidation = False
      self.ui.pushAddElucidation.hide()
      return

    self.ui.pushAddElucidation.show()

  def on_pushAddElucidation_pressed(self):
    self.load_elucidation = True
    self.ui.pushAddElucidation.hide()
    text_ID = self.selected_item.text(0)
    predicate = self.selected_item.predicate
    if self.__hasElucidation(text_ID, predicate):
      p = self.__makePathName(text_ID)
      d = self.ui.textElucidation.toPlainText()
      self.elucidations[p] = d
      pass

  def __makePathName(self, text_ID):
    p = self.root_class
    for i in self.class_path[1:]:
      p = p + ".%s" % i
    if text_ID not in p:
      item_name = text_ID
      p = p + ".%s" % item_name
    return p

  def __isClass(self, ID):
    return ID in self.class_names

  def __isSubClass(self, ID):
    return ID in self.subclass_names[self.current_class]

  def __isPrimitive(self, text_ID):
    print("debugging -- is primitive", text_ID)
    return text_ID in PRIMITIVES

  def __isValue(self, predicate):
    return predicate == "value"

  def __islinked(self, ID):
    for cl in self.link_lists:
      for linked_class, linked_to_class, linked_to_subclass in self.link_lists[cl]:
        if linked_to_class == self.current_class:
          if linked_to_subclass == ID:
            return True

    return False

  def __hasElucidation(self, text_ID, predicate):
    return self.__isClass(text_ID) or self.__isSubClass(text_ID) or self.__isValue(predicate)

  def on_pushAddSubclass_pressed(self):
    print("debugging -- add subclass")

    # get an identifier for the subclass
    forbidden = sorted(self.subclass_names[self.current_class]) + sorted(self.class_names)
    dialog = UI_String("name for subclass", limiting_list=forbidden)
    dialog.exec_()
    subclass_ID = dialog.getText()

    if not subclass_ID:
      return


    # keep track of names
    self.subclass_names[self.current_class].append(subclass_ID)
    self.primitives[self.current_class][self.current_subclass] = []

    # elucidation
    p = self.__makePathName(subclass_ID)
    self.elucidations[p] = None
    self.ui.textElucidation.clear()

    # add to graph
    subject = makeRDFCompatible(subclass_ID)
    object = makeRDFCompatible(self.current_subclass)
    predicate = "is_a_subclass_of"
    self.CLASSES[self.current_class].add((subject, RDFSTerms["is_a_subclass_of"], object))

    # generate GUI tree
    parent_item = self.ui.treeClass.currentItem()
    item = QTreeWidgetItem(parent_item)
    item.predicate = predicate
    item.setText(0, subclass_ID)
    self.ui.treeClass.expandAll()
    self.changed = True

  def on_pushAddPrimitive_pressed(self):
    # print("debugging -- add primitive")
    forbidden = self.subclass_names[self.current_class]  # TODO: no second linked primitive allowed
    dialog = UI_String("name for primitive", limiting_list=forbidden)
    dialog.exec_()
    primitive_ID = dialog.getText()
    if not primitive_ID:
      return

    permitted_classes = PRIMITIVES
    dialog = SingleListSelector(permitted_classes)
    dialog.exec_()
    primitive_class = dialog.getSelection()
    # print("debugging")
    if not primitive_class:
      return

    # add to graph
    item = self.__addItemToTree(primitive_ID, "value", self.current_subclass)
    self.__addItemToTree(primitive_class, primitive_class, primitive_ID, parent_item=item)
    if self.current_subclass not in self.primitives[self.current_class]:
      self.primitives[self.current_class][self.current_subclass] = []
    self.primitives[self.current_class][self.current_subclass].append(primitive_ID)

  def __addItemToTree(self, internal_object, predicate, internal_subject, parent_item=None):
    object = makeRDFCompatible(internal_object)
    subject = makeRDFCompatible(internal_subject)
    self.CLASSES[self.current_class].add((subject, RDFSTerms[predicate], object))
    # generate GUI tree
    if not parent_item:
      parent_item = self.ui.treeClass.currentItem()
    item = QTreeWidgetItem(parent_item)
    item.setText(0, internal_object)
    item.setBackground(0, PRIMITIVE_COLOUR)
    self.ui.treeClass.expandAll()
    self.changed = True
    return item

  def on_pushAddNewClass_pressed(self):
    # print("debugging -- add class")

    forbidden = sorted(self.class_names)
    dialog = UI_String("name for subclass", limiting_list=forbidden)
    dialog.exec_()
    class_ID = dialog.getText()
    if not class_ID:
      return

    self.CLASSES[class_ID] = Graph('Memory', Literal(class_ID))
    self.class_definition_sequence.append(class_ID)
    self.subclass_names[class_ID] = []
    self.primitives[class_ID] = {class_ID: []}


    # elucidation
    self.ui.textElucidation.clear()
    self.elucidations[class_ID] = None

    # make link
    subject = makeRDFCompatible(class_ID)
    object = makeRDFCompatible(self.current_subclass)
    self.CLASSES[self.current_class].add((subject, RDFSTerms["link_to_class"], object))

    if class_ID not in self.link_lists:
      self.link_lists[class_ID] = []
    self.link_lists[class_ID].append((class_ID, self.current_class, self.current_subclass))

    self.__createTree(class_ID)
    self.class_names.append(class_ID)
    self.__addToClassPath(addclass=class_ID)
    self.current_class = class_ID
    self.class_definition_sequence.append(class_ID)
    self.primitives[class_ID] = {"root": []}
    self.changed = True

  def on_pushAddExistingClass_pressed(self):
    # print("debugging -- pushExistingClass")
    permitted_classes = self.__permittedClasses()

    # print("debugging -- ", permitted_classes)
    if permitted_classes:
      dialog = SingleListSelector(permitted_classes)
      dialog.exec_()
      selection = dialog.getSelection()
      # print("debugging")
      if not selection:
        return

      class_ID = selection
      subject = makeRDFCompatible(class_ID)
      object = makeRDFCompatible(self.current_subclass)
      self.CLASSES[self.current_class].add((subject, RDFSTerms["link_to_class"], object))

      if class_ID not in self.link_lists:
        self.link_lists[class_ID] = []
      self.link_lists[class_ID].append((class_ID, self.current_class, self.current_subclass))

      parent_item = self.ui.treeClass.currentItem()
      item = QTreeWidgetItem(parent_item)
      item.setText(0, class_ID)
      columns = item.columnCount()
      item.setBackground(0, LINK_COLOUR)
      self.ui.treeClass.expandAll()
      self.changed = True

  def __permittedClasses(self):
    permitted_classes = []
    for cl in self.CLASSES:
      if cl != self.current_class:
        if cl not in self.link_lists[cl]:
          if cl not in self.class_path:
            permitted_classes.append(cl)
    return permitted_classes

  def __addToClassPath(self, addclass):
    self.class_path.append(addclass)
    self.ui.listClasses.clear()
    self.ui.listClasses.addItems(self.class_path)

  def __cutClassPath(self, cutclass):
    i = self.class_path.index(cutclass)
    self.class_path = self.class_path[:i + 1]
    self.ui.listClasses.clear()
    self.ui.listClasses.addItems(self.class_path)

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
    # f = self.TTLFile.split(".")[0] + ".nqd"
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

    saveWithBackup(data, self.TTLFile)

    # graphs = Graph("Memory")
    # for cl in self.class_definition_sequence:
    #   # graphs[cl] = []
    #   for t in self.CLASSES[cl].triples((None, None, None)):
    #     graphs.add(t)
    #
    # self.TTLFile = self.TTLFile.split(".ttl")[0] + ".nquads"
    #
    # graphs.serialize(TTLFile, format="nquads")
    # saveWithBackup(graphs, TTLFile)
    # self.changed = False

    self.changed = False

  # def saveAs(self):
  #   print("not implemented")

  def on_pushLoad_pressed(self):
    options = QFileDialog.Options()
    dialog = QFileDialog.getOpenFileName(None,
                                         "Load Ontology",
                                         TTLDirectory,
                                         "",
                                         # "Turtle files (*.ttl)",
                                         "triple files (*.json",
                                         # options=options
                                         )
    self.TTLFile = dialog[0]
    if dialog[0] == "":
      self.close()

    # print("debugging")
    data = getData(self.TTLFile)
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

  def on_pushVisualise_pressed(self):

    graph_overall = Graph()
    for cl in self.CLASSES:
      for t in self.CLASSES[cl].triples((None, None, None)):
        graph_overall.add(t)

    dot = plot(graph_overall, self.class_names)
    # print("debugging -- dot")
    dot.render("graph", directory=TTLDirectory)
    dot.view()


if __name__ == "__main__":
  import sys

  app = QApplication(sys.argv)

  icon_f = "task_ontology_foundation.svg"
  icon = os.path.join(os.path.abspath("resources/icons"), icon_f)
  app.setWindowIcon(QtGui.QIcon(icon))

  MainWindow = OntobuilderUI()
  MainWindow.show()
  sys.exit(app.exec_())
