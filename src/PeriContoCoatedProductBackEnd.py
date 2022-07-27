
import os

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


from graphviz import Digraph
from rdflib import Graph
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS
from rdflib import XSD


def prepareTree(graph):
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


class BackEnd:
  def __init__(self, FrontEnd ):

    self.FrontEnd = FrontEnd
    self.ontology_graph = None
    self.ontology_root = None
    self.changed = False

    self.ui_state("start")
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
    pass

  def processEvent(self, Event, event_data):

    if Event == "":
      pass
    elif Event == "create":
      self.FrontEnd.dialog("gotten_ontology_file_name",
                           "name for your ontology file",
                           "file name -- extension is defaulted",
                           [],
                           "exit" )

    elif Event == "gotten_ontology_file_name":
      self.dialogJsonDataFile(event_data)
      self.FrontEnd.dialog("gotten_root",
                           "root identifier",
                           "provide an identifier for the root",
                           [],
                           "exit")
    elif Event == "gotten_root":
      self.__makeRoot(event_data)
    elif Event == "data_file":
      self.dialogJsonDataFile(event_data)
    elif Event == "shift_class":
      self.shiftClass(event_data)


  def shiftClass(self, class_ID):
    self.current_class = class_ID
    if class_ID not in self.class_path:
      self.listClasses.append(class_ID)
      self.FrontEnd.populate("selectors","classList", self.listClasses)
    else:
      i = self.class_path.index(class_ID)
      self.class_path = self.class_path[:i + 1]
      self.clear()
      self.ui.listClasses.addItems(self.class_path)

  def dialogJsonDataFile(self, name):
    file_name = name.split(".")[0] + ".json"
    self.JsonFile = os.path.join(ONTOLOGY_DIRECTORY, file_name)

  def __makeRoot(self, name):

    self.root_class = name
    self.CLASSES = {self.root_class: Graph('Memory', Literal(self.root_class))}
    self.current_class = self.root_class
    self.subclass_names[self.root_class] = [self.root_class]
    self.class_names.append(self.root_class)
    self.class_path = [self.root_class]
    self.link_lists[self.root_class] = []
    self.listClasses = [self.class_path]
    # self.ui.listClasses.addItems(self.class_path)
    self.class_definition_sequence.append(self.root_class)
    self.primitives[self.root_class] = {self.root_class: []}
    self.changed = True

    graph = self.CLASSES[self.current_class]
    self.truples = prepareTree(graph)
    self.FrontEnd.populate("selectors", "classTree", self.truples,self.root_class)
    # self.FrontEnd.processCallBack("populate","selectors", "classTree", self.truples,self.root_class)
    # self.FrontEnd.gui_objects_controls["selectors"]["classes"]["populate"](self.truples,self.root_class)
    # self.FrontEnd.makeClassTree(self.truples, self.root_class)

  def __makeClassList(self):
    self.FrontEnd.populate("selector", "classTree", self.listClasses)
    pass



  def ui_state(self, state):
    # what to show and clear
    clear = { }
    if state == "start":
      show = {"buttons": ["load",
              "create",
              "exit",
              ]}
      clear = {"selectors": ["classList", "classTree"] }
    elif state == "show_tree":
      show = {"buttons": ["save",
              "exit",
              "visualise",
              ]}
    elif state == "selected_subclass":
      show = {"buttons": ["save",
              "exit",],
              "textEdit": ["ClassSubclassElucidation",
              ]}
    elif state == "selected_class":
      show = {"buttons": ["save",
              "exit",],
              "groups": [
              "ValueElucidation", "PrimitiveString"],
              }
    elif state == "selected_integer":
      show = {"buttons": ["save",
              "exit",],
              "groups": [
              "ValueElucidation",
              "PrimitiveQuantity",
              ]
              }
    elif state == "selected_string":
      show = {"buttons": ["save",
              "exit",],
              "groups": [
              "ValueElucidation",
              "PrimitiveString",
              ]
              }
    elif state == "selected_value":
      show = {"buttons": ["save",
              "exit",],
              "groups": [
              "ValueElucidation",
              ]
              }
    else:
      show = []
      print("ooops -- no such state", state)

    gui_obj = self.FrontEnd.gui_objects

    for c in gui_obj:
      k = list(gui_obj[c].keys())
      for b in k:
        gui_obj[c][b].hide()
    for c in show:
      for b in show[c]:
        gui_obj[c][b].show()

    # for c in clear:
    #   for b in clear[c]:
    #     if b not in clear[c]:
    #       self.FrontEnd.gui_objects[c][b].hide()
    #     else:
    #       self.FrontEnd.gui_objects[c][b].show()

