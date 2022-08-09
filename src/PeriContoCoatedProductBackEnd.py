"""
Backend to the construction of a data base for coatings formulations

The data are stored in triple stored in triple stores

rule: notation
an instantiated "node" is <<name>>:<<ID>>

"""

DELIMITERS = {"instantiated": ":"}

from rdflib import Graph,Literal

# from PeriConto import COLOURS
# from PeriConto import LINK_COLOUR
from PeriConto import MYTerms
from PeriConto import ONTOLOGY_DIRECTORY
from PeriConto import PRIMITIVES
# from PeriConto import PRIMITIVE_COLOUR
from PeriConto import RDFSTerms
from PeriConto import VALUE
# from PeriConto import VALUE
from PeriConto import getData
from PeriConto import makeRDFCompatible


# from PeriConto import plot
# from PeriConto import saveWithBackup
# # from graphHAP import Graph
# from PeriContoCoatedProduct_gui import Ui_MainWindow
# from resources.pop_up_message_box import makeMessageBox
# from resources.resources_icons import roundButton
# from resources.single_list_selector_impl import SingleListSelector
# from resources.ui_string_dialog_impl import UI_String


def prepareTree(graph, graph_ID):
  """
  The truples are not triples, but non-directed graph nodes augmented with predicate an node identifier
  """
  truples = []
  for subject, predicate, object_ in graph.triples((None, None, None)):
    s = str(subject)
    p = MYTerms[predicate]
    o = str(object_)
    if p not in ["value"] + PRIMITIVES:
      truples.append((s, o, p, graph_ID))
    else:
      truples.append((o, s, p, graph_ID))
  return truples

def convertRDFintoInternalGraph(rdf_graph, root):
  graph = []


class SuperGraph():
  def __init__(self):
    self.root_class = None
    self.class_path = []
    self.class_names = []
    self.subclass_names = {}
    self.link_lists = {}
    self.CLASSES = {}
    self.class_definition_sequence = []
    self.primitives = {}
    self.root_class = None
    self.elucidations = {}
    self.JsonFile = None

  def create(self, root_class):
    self.root_class = root_class
    self.CLASSES = {self.root_class: Graph('Memory', Literal(self.root_class))}
    self.current_class = self.root_class
    self.subclass_names[self.root_class] = [self.root_class]
    self.class_names.append(self.root_class)
    self.class_path = [self.root_class]
    self.link_lists[self.root_class] = []
    self.class_definition_sequence.append(self.root_class)
    self.primitives[self.root_class] = {self.root_class: []}

  def load(self, JsonFile):
    self.JsonFile = JsonFile
    data = getData(self.JsonFile)
    self.root_class = data["root"]
    self.elucidations = data["elucidations"]

    graphs_internal = data["graphs"]
    for g in graphs_internal:
      self.class_definition_sequence.append(g)
      self.class_names.append(g)
      self.subclass_names[g] = []
      self.primitives[g] = {g: []}
      self.link_lists[g] = []
      self.CLASSES[g] = Graph()
      for s, p, o in graphs_internal[g]:
        self.addGraphGivenInInternalNotation(g, s, p, o)

    self.subclass_names = {}
    self.link_lists = {}
    self.value_lists = {}
    self.integer_lists = {}
    self.string_lists = {}
    self.comment_lists = {}

    for rdf_graph_ID in self.CLASSES:
      rdf_graph = self.CLASSES[rdf_graph_ID]
      self.subclass_names[rdf_graph] = makeListBasedOnPredicates(rdf_graph, "is_a_subclass_of")
      self.link_lists[rdf_graph] = makeListBasedOnPredicates(rdf_graph, "link_to_class")
      self.value_lists[rdf_graph] = makeListBasedOnPredicates(rdf_graph, "value")
      self.integer_lists[rdf_graph] = makeListBasedOnPredicates(rdf_graph, "integer")
      self.integer_lists[rdf_graph] = makeListBasedOnPredicates(rdf_graph, "integer")
      self.string_lists[rdf_graph] = makeListBasedOnPredicates(rdf_graph, "string")
      self.comment_lists[rdf_graph] = makeListBasedOnPredicates(rdf_graph, "comment")

    return self.root_class

  def addGraphGivenInInternalNotation(self, graph_ID, subject_internal, predicate_internal, object_internal):
    rdf_subject = makeRDFCompatible(subject_internal)
    rdf_object = makeRDFCompatible(object_internal)
    rdf_predicate = RDFSTerms[predicate_internal]
    self.CLASSES[graph_ID].add((rdf_subject, rdf_predicate, rdf_object))

  def makePathName(self, text_ID):
    p = self.root_class
    for i in self.class_path[1:]:
      p = p + ".%s" % i
    if text_ID not in p:
      item_name = text_ID
      p = p + ".%s" % item_name
    return p

  def isClass(self, ID):
    return ID in self.class_names

  def isSubClass(self, ID, graph_class):
    # graph_class is the currently active class
    return (ID in self.subclass_names[graph_class]) and \
           (ID not in self.class_names)

  def isPrimitive(self, text_ID):
    # print("debugging -- is primitive", text_ID)
    return text_ID in PRIMITIVES

  def isValue(self, predicate):
    return predicate == VALUE

  def isLinked(self, ID, graph_class):
    # graph_class is the currently active class
    for cl in self.link_lists:
      for linked_class, linked_to_class, linked_to_subclass in self.link_lists[cl]:
        if linked_to_class == graph_class:
          if linked_to_subclass == ID:
            return True

  def isInstantiated(self, ID):
    return DELIMITERS["instantiated"] in ID


def makeListBasedOnPredicates(rdf_graph, rdf_predicate):
  subclasslist = []
  for s, p, o in rdf_graph.triples((None, RDFSTerms[rdf_predicate], None)):
    subclasslist.append(s)
  return subclasslist


class ContainerGraph(SuperGraph):

  def __init__(self):
    SuperGraph.__init__(self)
    pass








class DataGraph(SuperGraph):

  def __init__(self):
    SuperGraph.__init__(self)
    pass

  def add(self):
    pass


class BackEnd:

  def __init__(self, FrontEnd):

    global state

    self.FrontEnd = FrontEnd
    self.ontology_graph = None
    self.ontology_root = None
    self.changed = False

    self.ContainerGraph = ContainerGraph()
    self.data_container = {}

    self.ui_state("start")
    self.event_data = None
    self.current_node = None
    self.data_tree_root_node = None

    self.current_class = None
    self.current_subclass = None
    self.current_item_text_ID = None
    self.identifiers = {}
    # self.subclass_names = {}
    # self.primitives = {}
    # self.class_names = []
    self.class_path = []
    self.path = []
    # self.link_lists = {}
    self.class_definition_sequence = []
    self.TTLfile = None
    # self.elucidations = {}
    self.selected_item = None
    # self.root_class = None
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
            "got_ontology_file_name": {"file_name": {"next_state": "show_tree",
                                                     "actions"   : [self.__1_loadOntology,
                                                                    self.__createDataTree,
                                                                    self.__makeDataTree,
                                                                    # self.__2_getIdentifier,
                                                                    ],
                                                     "gui_state" : "show_tree"},
                                       },
            "show_tree"             : {"selected": {"next_state": "check_selection",
                                                    "actions"   : [self.__selectedItem,
                                                                   self.__checkSelection],
                                                    "gui_state" : "show_tree"},
                                       },
            "check_selection"       : {"selected": {"next_state": "wait_for_ID",
                                                    "actions"   : [None],
                                                    "gui_state" : "checked_selection"},
                                       },
            "wait_for_ID"           : {"has_no_ID"  : {"next_state": "wait_for_ID",
                                                       "actions"   : [None],
                                                       "gui_state" : "has_no_ID"},
                                       "has_ID"     : {"next_state": "wait_for_ID",
                                                       "actions"   : [None],
                                                       "gui_state" : "has_ID"},
                                       "got_no_ID"  : {"next_state": "show_tree",
                                                       "actions"   : [None],
                                                       "gui_state" : "show_tree"},
                                       "add_new_ID" : {"next_state": "show_tree",
                                                       "actions"    : [self.__updateDataWithNewID],
                                                       "gui_state" : "show_tree"},
                                       "selected_ID": {"next_state": "show_tree",
                                                       "actions"    : [self.__updateTree],
                                                       "gui_state" : "show_tree"},
                                       },
            # "state"      : {"event": {"next_state": add next state,
            #                                                "actions"   : [list of actions],
            #                                                "gui_state" : specify gui shows (separate dictionary}},
            #                          },
            # "state"      : {"event": {"next_state": add next state,
            #                                                "actions"   : [list of actions],
            #                                                "gui_state" : specify gui shows (separate dictionary}},
            #                          },
            }
    pass

    # self.processEvent("start", "initialise", None)

  def processEvent(self, state, Event, event_data):
    # Note: cannot be called from within backend -- generates new name space
    global gui_state

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
          "\n             data    :", event_data,
          "\n")

    for action in actions:
      if action:
        action(next_state, event_data)  # Note: state info must be carried along due to callback
    self.ui_state(gui_state)

    return next_state

  def __0_askForFileName(self, state, event_data):

    self.FrontEnd.fileNameDialog(state, "file_name",
                                 "ontology",
                                 ONTOLOGY_DIRECTORY,
                                 "*.json",
                                 "exit")

  def __1_loadOntology(self, state, event_data):
    self.root_class_container = self.ContainerGraph.load(event_data)


  def __selectedItem(self, state, data):
    """
    data is a list with selected item ID, associated predicate and a graph ID
    """
    self.current_node = data[0]

  def __checkSelection(self, state, data):

    s,p,o, graph_ID = data
    item_ID = o
    predicate = p
    is_class = self.data_container[self.current_data_tree].isClass(item_ID)
    is_sub_class = self.data_container[self.current_data_tree].isSubClass(item_ID, self.current_class)
    is_primitive = self.data_container[self.current_data_tree].isPrimitive(item_ID)
    is_value = self.data_container[self.current_data_tree].isValue(predicate)
    is_linked = self.data_container[self.current_data_tree].isLinked(item_ID, self.current_class)
    is_instantiated = self.data_container[self.current_data_tree].isInstantiated(item_ID)

    s = "selection has data: %s    " % data

    if is_class: s += " & class"
    if is_sub_class: s += " & subclass"
    if is_primitive: s += " & primitive"
    if is_value: s += " & value"
    if is_linked: s += " & is_linked"
    if is_instantiated: s += " & instantiated"
    print("selection : %s\n" % s)

    if is_class or is_sub_class:
      if is_instantiated:
        self.ui_state("has_ID")
      else:
        self.ui_state("has_no_ID")

  # def __makeTriple(self):
  #   triple = (self.current_node, "is_a", self.)

  # def __4_getAllIdentifiers(self, state, event_data):
  #   for g in self.CLASSES:
  #     self.identifiers[g] = []
  #     for s, p, o in self.CLASSES[g].triples((None, RDFSTerms["value"], None)):  # RDFSTerms["string"])):
  #       print("found", s, p, o)
  #       if "Identifier" in o:
  #         self.identifiers[g].append(str(s))
  #   pass

  # def __5_showDataTree(self, state, event_data):

  def __updateDataWithNewID(self,state, data):
    print("debugging -- new ID", state, data)

  def __updateTree(self, state, data):
    print("debugging -- selected ID", state, data)

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

  def __createDataTree(self, state, data):

    if not self.data_container:
      self.data_container = {1: DataGraph()}
      self.current_data_tree = 1
      root_class = self.root_class_container + DELIMITERS["instantiated"] + str(1)
      self.data_container[1].create(root_class)
      self.current_class = root_class
      container_graph = self.ContainerGraph.CLASSES[self.root_class_container]
      for s,p,o in container_graph.triples((None,None,None)):
        if str(s) == self.root_class_container:
          s_ = Literal(root_class)
        else:
          s_ = s
        if str(o) == self.root_class_container:
          o_ = Literal(root_class)
        else:
          o_ = o
        data_graph = self.data_container[1].CLASSES[root_class]
        data_graph.add((s_,p,o_))
      pass

  def __makeDataTree(self, state, data):

    graph = self.data_container[self.current_data_tree].CLASSES[self.current_class]
    self.truples = prepareTree(graph, "data %s"%self.current_data_tree)
    self.FrontEnd.controls("selectors", "classTree", "populate", self.truples, str(graph.identifier))
    self.__makeClassList()

  # def __makeTree(self, state, data):
  #
  #
  #   # self.root_class = name
  #   # self.CLASSES = {self.root_class: Graph('Memory', Literal(self.root_class))}
  #   # self.current_class = self.root_class
  #   # self.subclass_names[self.root_class] = [self.root_class]
  #   # self.class_names.append(self.root_class)
  #   # self.class_path = [self.root_class]
  #   # self.link_lists[self.root_class] = []
  #   # self.listClasses = [self.class_path]
  #   # # self.ui.listClasses.addItems(self.class_path)
  #   # self.class_definition_sequence.append(self.root_class)
  #   # self.primitives[self.root_class] = {self.root_class: []}
  #   # self.changed = True
  #
  #   graph = self.ContainerGraph.CLASSES[self.current_class]
  #   self.truples = prepareTree(graph, "container")
  #   self.FrontEnd.controls("selectors", "classTree", "populate", self.truples, self.root_class_container)
  #   self.__makeClassList()

  def __makeClassList(self):
    path = self.data_container[self.current_data_tree].class_path
    self.FrontEnd.controls("selectors", "classList", "populate", path)
    pass

  def ui_state(self, state):
    # what to show and clear
    clear = {}
    if state == "start":
      show = {"buttons": ["load",
                          "create",
                          "exit",
                          ], }
      clear = {"selectors": ["classList", "classTree"]}
    elif state == "initialise":
      show = {"buttons"  : ["load",
                            "create",
                            "exit",
                            ],
              "selectors": ["classList",
                            "classTree"]}
    elif state == "input_identifier":
      show = {"buttons": ["exit",
                          ],
              "groups" : [
                      "PrimitiveString"], }
    elif state == "show_tree":
      show = {"buttons"  : ["save",
                            "exit",
                            "visualise",
                            ],
              "selectors": ["classList",
                            "classTree"],
              }
    elif state == "checked_selection":
      show = {"buttons"  : ["save",
                            "exit",
                            "visualise",
                            "instantiate",
                            ],
              "selectors": ["classList",
                            "classTree"],
              }
    elif state == "instantiate_item":
      show = {"buttons"  : ["instantiate",
                            ],
              "selectors": ["classList",
                            "classTree",
                            "integer"],
              "groups"   : "integer"}
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
                      "integer",
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
      print("ooops -- no such gui state", state)

    print("debugging -- state & show", state, show)

    objs = self.FrontEnd.gui_objects
    obj_classes = list(objs.keys())
    for oc in obj_classes:
      o_list = list(objs[oc].keys())
      for o in o_list:
        self.FrontEnd.controls(oc, o, "hide")
      for o in o_list:
        if oc in show:
          if o in show[oc]:
            self.FrontEnd.controls(oc,o,"show")


  # ====================  attic

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

  # def __2_getIdentifier(self, state, data):
  #   self.FrontEnd.dialog(state, "identifier",
  #                        "give identifier",
  #                        "identifier",
  #                        [],
  #                        "exit"
  #                        )

  # def __3_makeDataTreeRootNode(self, state, data):
  #   self.data_tree_root_node = "%s@%s" % (self.root_class, data)
  #   print("debugging -- data tree root node", self.data_tree_root_node)
  #   self.current_node = self.data_tree_root_node

  # def __dialogJsonDataFile(self, name):
  #   file_name = name.split(".")[0] + ".json"
  #   return os.path.join(ONTOLOGY_DIRECTORY, file_name)
