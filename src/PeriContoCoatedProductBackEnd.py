import os

from rdflib import Graph

# from PeriConto import COLOURS
# from PeriConto import LINK_COLOUR
from PeriConto import MYTerms
from PeriConto import ONTOLOGY_DIRECTORY
from PeriConto import PRIMITIVES
# from PeriConto import PRIMITIVE_COLOUR
from PeriConto import RDFSTerms
# from PeriConto import VALUE
from PeriConto import getData
from PeriConto import makeRDFCompatible
from rdflib import Literal


# from PeriConto import plot
# from PeriConto import saveWithBackup
# # from graphHAP import Graph
# from PeriContoCoatedProduct_gui import Ui_MainWindow
# from resources.pop_up_message_box import makeMessageBox
# from resources.resources_icons import roundButton
# from resources.single_list_selector_impl import SingleListSelector
# from resources.ui_string_dialog_impl import UI_String


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
  def __init__(self, FrontEnd):

    self.FrontEnd = FrontEnd
    self.ontology_graph = None
    self.ontology_root = None
    self.changed = False

    self.ui_state("start")
    self.event_data = None
    self.current_node = None
    self.data_tree_root_node = None

    self.current_class = None
    self.current_subclass = None
    self.current_item_text_ID = None
    self.identifiers = {}
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

    self.automaton = {
            "start"                 : {"initialise": {"next_state": "initialised",
                                                      "actions"   : [None],
                                                      "gui_state" : "start"},
                                       },
            "initialised"           : {"create": {"next_state": "got_ontology_file_name",
                                                  "actions"   : [self.__0_askForFileName],
                                                  "gui_state" : "initialise"},
                                       },
            "got_ontology_file_name": {"file_name": {"next_state": "make_data_tree_node",
                                                     "actions"   : [self.__1_loadOntology,
                                                                    self.__2_getIdentifier,],
                                                     "gui_state" : "initialise"},
                                       },
            "make_data_tree_node"      : {"identifier": {"next_state": "show_enabled_tree",
                                                           "actions"   : [self.__3_makeDataTreeRootNode,
                                                                          self.__4_getAllIdentifiers],
                                                           "gui_state" : "input_identifier"}},

            "show_enabled_tree"      : {"identifier": {"next_state": "show_enabled_tree",
                                                           "actions"   : [self.__getAllIdentifiers],
                                                           "gui_state" : "input_identifier"}}

            }
    pass

    self.processEvent("start", "initialise", None)


  def processEvent(self, state, Event, event_data):
    if state not in self.automaton:
      print("stopping here - no such state", state)
      return
    if Event not in self.automaton[state]:
      print("stopping here - no such event", Event, "  at state", state)
      return

    next_state = self.automaton[state][Event]["next_state"]
    actions = self.automaton[state][Event]["actions"]
    gui_state = self.automaton[state][Event]["gui_state"]

    print("automaton -- ",
          "\n             state   :", state,
          "\n             next    :", next_state,
          "\n             actions :", actions,
          "\n             gui     :", gui_state,
          "\n")

    for action in actions:
      if action:
        action(next_state, event_data)   # Note: state info must be carried along due to callback
    self.ui_state(gui_state)

    return next_state

  def __0_askForFileName(self, state, event_data):

    self.FrontEnd.fileNameDialog(state, "file_name",
                                 "ontology",
                                 ONTOLOGY_DIRECTORY,
                                 "*.json",
                                 "exit")


  def __1_loadOntology(self, state, event_data):
    self.JsonFile = event_data
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




    print("ontology loaded, state is", state)
    self.current_node = self.root_class

    # self.FrontEnd.controls("selectors", "classList", "populate", self.class_path)

  def __2_getIdentifier(self, state, data):
    self.FrontEnd.dialog(state, "identifier",
                                 "give identifier",
                                 "identifier",
                                 [],
                         "exit"
                         )

  def __3_makeDataTreeRootNode(self, state, data):
    self.data_tree_root_node = "%s@%s"%(self.root_class, data)
    print("debugging -- data tree root node", self.data_tree_root_node)
    self.current_node = self.data_tree_root_node


  # def __makeTriple(self):
  #   triple = (self.current_node, "is_a", self.)


  def __4_getAllIdentifiers(self, state, event_data):
    for g in self.CLASSES:
      self.identifiers[g] = []
      for s,p,o in self.CLASSES[g].triples((None, RDFSTerms["value"], None)): #RDFSTerms["string"])):
        print("found", s,p,o)
        if "Identifier" in o:
          self.identifiers[g].append(str(s))
    pass

  def __5_showDataTree(self, state, event_data):


  def shiftClass(self, class_ID):
    self.current_class = class_ID
    if class_ID not in self.class_path:
      self.listClasses.append(class_ID)
      self.FrontEnd.populate("selectors", "classList", self.listClasses)
    else:
      i = self.class_path.index(class_ID)
      self.class_path = self.class_path[:i + 1]
      # self.FrontEnd.
      # self.clear()
      # self.ui.listClasses.addItems(self.class_path)

  # def __dialogJsonDataFile(self, name):
  #   file_name = name.split(".")[0] + ".json"
  #   return os.path.join(ONTOLOGY_DIRECTORY, file_name)

  def __makeTree(self, name):

    # self.root_class = name
    # self.CLASSES = {self.root_class: Graph('Memory', Literal(self.root_class))}
    # self.current_class = self.root_class
    # self.subclass_names[self.root_class] = [self.root_class]
    # self.class_names.append(self.root_class)
    # self.class_path = [self.root_class]
    # self.link_lists[self.root_class] = []
    # self.listClasses = [self.class_path]
    # # self.ui.listClasses.addItems(self.class_path)
    # self.class_definition_sequence.append(self.root_class)
    # self.primitives[self.root_class] = {self.root_class: []}
    # self.changed = True

    graph = self.CLASSES[self.current_class]
    self.truples = prepareTree(graph)
    self.FrontEnd.controls("selectors", "classTree", "populate", self.truples, self.root_class)
    # self.FrontEnd.processCallBack("populate","selectors", "classTree", self.truples,self.root_class)
    # self.FrontEnd.gui_objects_controls["selectors"]["classes"]["populate"](self.truples,self.root_class)
    # self.FrontEnd.makeClassTree(self.truples, self.root_class)

  def __makeClassList(self):
    self.FrontEnd.populate("selector", "classTree", self.listClasses)
    pass

  def ui_state(self, state):
    # what to show and clear
    clear = {}
    if state == "start":
      show = {"buttons": ["load",
                          "create",
                          "exit",
                          ]}
      clear = {"selectors": ["classList", "classTree"]}
    elif state == "initialise":
      show = {"buttons": ["load",
                          "create",
                          "exit",
                          ]}
    elif state == "input_identifier":
      show = {"buttons": ["exit",
                          ],
              "groups" : [
                      "PrimitiveString"], }
    elif state == "show_tree":
      show = {"buttons": ["save",
                          "exit",
                          "visualise",
                          ]}
    elif state == "selected_subclass":
      show = {"buttons" : ["save",
                           "exit", ],
              "textEdit": ["ClassSubclassElucidation",
                           ]}
    elif state == "selected_class":
      show = {"buttons": ["save",
                          "exit", ],
              "groups" : [
                      "ValueElucidation", "PrimitiveString"],
              }
    elif state == "selected_integer":
      show = {"buttons": ["save",
                          "exit", ],
              "groups" : [
                      "ValueElucidation",
                      "PrimitiveQuantity",
                      ]
              }
    elif state == "selected_string":
      show = {"buttons": ["save",
                          "exit", ],
              "groups" : [
                      "ValueElucidation",
                      "PrimitiveString",
                      ]
              }
    elif state == "selected_value":
      show = {"buttons": ["save",
                          "exit", ],
              "groups" : [
                      "ValueElucidation",
                      ]
              }
    else:
      show = []
      print("ooops -- no such state", state)

    objs = self.FrontEnd.gui_objects
    obj_classes = list(objs.keys())
    for oc in obj_classes:
      if oc == "buttons":
        buttons = objs[oc]
        for b in buttons:
          if b in show["buttons"]:
            self.FrontEnd.controls("buttons", b, "show")
          else:
            self.FrontEnd.controls("buttons", b, "hide")
      else:
        o_list = list(objs[oc].keys())
        for o in o_list:
          # print(oc, o)
          self.FrontEnd.controls(oc, o, "hide")



  # def __processEvent(self, Event, event_data):
  #
  #   if Event == "":
  #     pass
  #   elif Event == "load":
  #     print("not-yet implemented -- load")
  #     pass
  #
  #   elif Event == "create":
  #     # self.FrontEnd.dialog("gotten_ontology_file_name",
  #     #                      "name for your ontology file",
  #     #                      "file name -- extension is defaulted",
  #     #                      [],
  #     #                      "exit" )
  #
  #     # self.FrontEnd.dialog("gotten_ontology_file_name",
  #     #                      "root identifier",
  #     #                      "provide an identifier for the root",
  #     #                      [],
  #     #                      "exit")
  #     self.FrontEnd.fileNameDialog("gotten_ontology_file_name",
  #                                  "ontology",
  #                                  ONTOLOGY_DIRECTORY,
  #                                  "*.json",
  #                                  "exit")
  #
  #   elif Event == "gotten_ontology_file_name":
  #     self.JsonFile = event_data  # self.__dialogJsonDataFile(event_data)
  #     self.__loadOntology()
  #     self.__makeTree(self.root_class)
  #     self.FrontEnd.controls("selectors", "classList", "populate", self.class_path)
  #
  #   elif Event == "selected_class":
  #     self.current_class = event_data
  #     self.__makeTree(self.current_class)
  #
  #   # elif Event == "gotten_root":
  #   #   self.__makeRoot(event_data)
  #   #   self.FrontEnd.controls("selectors","classTree","show")
  #
  #   # elif Event == "data_file":
  #   #   self.dialogJsonDataFile(event_data)
  #
  #   elif Event == "shift_class":
  #     self.shiftClass(event_data)