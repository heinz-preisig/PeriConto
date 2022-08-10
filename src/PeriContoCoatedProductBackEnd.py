"""
Backend to the construction of a data base for coatings formulations

The data are stored in triple stored in triple stores

rule: notation
an instantiated "node" is <<name>>:<<ID>>

"""

DELIMITERS = {"instantiated": ":"}

from rdflib import Graph
from rdflib import Literal

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


def convertRDFintoInternalMultiGraph(graph, graph_ID):
  """
  The quads are not triples, but non-directed graph nodes augmented with predicate an node identifier
  """
  quads = []
  for subject, predicate, object_ in graph.triples((None, None, None)):
    s = str(subject)
    p = MYTerms[predicate]
    o = str(object_)
    if p not in ["value"] + PRIMITIVES:
      quads.append((s, o, p, graph_ID))
    else:
      quads.append((o, s, p, graph_ID))
  return quads


# def isWhat(predicate):
#   ref_keys = set(RDFSTerms.keys())
#   if predicate in ref_keys:
#     return True
#   else:
#     return False


class SuperGraph():
  def __init__(self):
    self.JsonFile = None
    self.txt_root_class = None
    self.txt_class_path = []
    self.txt_class_names = []
    self.txt_subclass_names = {}
    self.txt_link_lists = {}
    self.class_definition_sequence = []
    self.txt_primitives = {}
    self.txt_elucidations = {}
    self.txt_value_lists = {}
    self.txt_integer_lists = {}
    self.txt_string_lists = {}
    self.txt_comment_lists = {}

    self.RDFConjunctiveGraph = {}

  def create(self, root_class):
    self.txt_root_class = root_class
    self.RDFConjunctiveGraph = {self.txt_root_class: Graph('Memory', identifier=root_class)}
    # self.RDFConjunctiveGraph = {self.txt_root_class: Graph('Memory', Literal(self.txt_root_class))}
    self.txt_subclass_names[self.txt_root_class] = [self.txt_root_class]
    self.txt_class_names.append(self.txt_root_class)
    self.txt_class_path = [self.txt_root_class]
    self.txt_link_lists[self.txt_root_class] = []
    self.class_definition_sequence.append(self.txt_root_class)
    self.txt_primitives[self.txt_root_class] = {self.txt_root_class: []}

  def load(self, JsonFile):
    """
    load conjunctive graph from json file and
    """
    self.JsonFile = JsonFile
    data = getData(self.JsonFile)
    self.txt_root_class = data["root"]
    self.txt_elucidations = data["elucidations"]

    graphs_internal = data["graphs"]
    for g in graphs_internal:
      self.class_definition_sequence.append(g)
      self.txt_class_names.append(g)
      self.txt_subclass_names[g] = []
      self.txt_primitives[g] = {g: []}
      self.txt_link_lists[g] = []
      # Note: defines the graph in a conjunctive graph. The rdflib.graph.ConjunctiveGraph seems to
      # Note:  show discrepancies between python implementation and documentation. Tried .get_graph
      self.RDFConjunctiveGraph[g] = Graph()

      # self.RDFConjunctiveGraph = rdflib.graph.ConjunctiveGraph( identifier=self.txt_root_class)

      for s, p, o in graphs_internal[g]:
        self.addGraphGivenInInternalNotation(s, p, o, g)

    self.makeAllLists()

    return self.txt_root_class

  def makeAllLists(self):
    for rdf_graph_ID in self.RDFConjunctiveGraph:
      rdf_graph = self.RDFConjunctiveGraph[rdf_graph_ID]
      # rdf_graph = self.RDFConjunctiveGraph.get_graph(rdf_graph_ID)

      self.txt_subclass_names[rdf_graph_ID] = makeListBasedOnPredicates(rdf_graph, "is_a_subclass_of")
      self.txt_link_lists[rdf_graph_ID] = makeLinkListBasedOnPredicates(rdf_graph, rdf_graph_ID, "link_to_class")
      self.txt_value_lists[rdf_graph_ID] = makeListBasedOnPredicates(rdf_graph, "value")
      self.txt_integer_lists[rdf_graph_ID] = makeListBasedOnPredicates(rdf_graph, "integer")
      self.txt_string_lists[rdf_graph_ID] = makeListBasedOnPredicates(rdf_graph, "string")
      self.txt_comment_lists[rdf_graph_ID] = makeListBasedOnPredicates(rdf_graph, "comment")
    pass

  def addGraphGivenInInternalNotation(self, subject_internal, predicate_internal, object_internal, graph_ID):
    rdf_subject = makeRDFCompatible(subject_internal)
    rdf_object = makeRDFCompatible(object_internal)
    rdf_predicate = RDFSTerms[predicate_internal]
    self.RDFConjunctiveGraph[graph_ID].add((rdf_subject, rdf_predicate, rdf_object))
    # self.RDFConjunctiveGraph.add((rdf_subject, rdf_predicate, rdf_object, self.txt_root_class))

  def makePathName(self, text_ID):
    p = self.txt_root_class
    for i in self.txt_class_path[1:]:
      p = p + ".%s" % i
    if text_ID not in p:
      item_name = text_ID
      p = p + ".%s" % item_name
    return p

  def isClass(self, ID):
    return ID in self.txt_class_names

  def isSubClass(self, ID, graph_class):
    # graph_class is the currently active class
    if graph_class in self.txt_subclass_names:
      return (ID in self.txt_subclass_names[graph_class]) and \
           (ID not in self.txt_class_names)
    else:
      return False

  def isPrimitive(self, text_ID):
    # print("debugging -- is primitive", text_ID)
    return text_ID in PRIMITIVES

  def isValue(self, predicate):
    return predicate == VALUE

  def isInteger(self, predicate):
    return predicate == "integer"

  def isComment(self, predicate):
    return (predicate == "comment")

  def isString(self, predicate):
    return (predicate == "comment")

  def isLinked(self, ID, graph_class):
    # graph_class is the currently active class
    for cl in self.txt_link_lists:
      for linked_class, linked_to_class, linked_to_subclass in self.txt_link_lists[cl]:
        if linked_to_class == graph_class:
          if linked_to_subclass == ID:
            return True

  def isInstantiated(self, ID):
    return DELIMITERS["instantiated"] in ID


def makeListBasedOnPredicates(rdf_graph, rdf_predicate):
  subclasslist = []
  for s, p, o in rdf_graph.triples((None, RDFSTerms[rdf_predicate], None)):
    subclasslist.append(str(s))  # (str(s), txt_class, str(o)))
  return subclasslist


def makeLinkListBasedOnPredicates(rdf_graph, txt_class, rdf_predicate):
  subclasslist = []
  for s, p, o in rdf_graph.triples((None, RDFSTerms[rdf_predicate], None)):
    subclasslist.append((str(s), txt_class, str(o)))
  return subclasslist


class ContainerGraph(SuperGraph):

  def __init__(self):
    SuperGraph.__init__(self)
    pass


class DataGraph(SuperGraph):

  def __init__(self):
    SuperGraph.__init__(self)
    pass


class BackEnd:

  def __init__(self, FrontEnd):

    global state
    # global class_path

    self.FrontEnd = FrontEnd
    # self.ontology_graph = None
    # self.ontology_root = None
    self.changed = False

    self.ContainerGraph = ContainerGraph()
    self.data_container = {}

    self.ui_state("start")
    self.event_data = None
    self.current_node = None
    # self.data_tree_root_node = None

    self.current_class = None
    self.current_subclass = None
    # self.current_item_text_ID = None
    # self.identifiers = {}
    # self.subclass_names = {}
    # self.primitives = {}
    # self.class_names = []
    # class_path = []
    class_path = []
    # self.path = []
    # self.link_lists = {}
    # self.class_definition_sequence = []
    # self.TTLfile = None
    # self.elucidations = {}
    # self.selected_item = None
    # self.root_class = None
    # self.load_elucidation = False
    # self.done = False
    # self.transition_points = {}  # keeps the information on where the transition to another class was made
    # self.complete_path = []
    # self.local_path = None
    # self.database = {}

    self.data_container = {}

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
                                                                    self.__makeDataTreeFromFile,
                                                                    # self.__2_getIdentifier,
                                                                    ],
                                                     "gui_state" : "show_tree"},
                                       },
            "show_tree"             : {"selected": {"next_state": "check_selection",
                                                    "actions"   : [self.__selectedItem,
                                                                   self.__checkSelection],
                                                    "gui_state" : "NoSet"},
                                       #                            },
                                       # "check_selection"       : {"selected": {"next_state": "wait_for_ID",
                                       #                                         "actions"   : [None],
                                       #                                         "gui_state" : "checked_selection"},
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
                                                       "actions"   : [self.__updateDataWithNewID],
                                                       "gui_state" : "show_tree"},
                                       "selected_ID": {"next_state": "show_tree",
                                                       "actions"   : [self.__updateTree],
                                                       "gui_state" : "show_tree"},
                                       },
            "class_list_clicked"      : {"selected": {"next_state": "show_tree",
                                                           "actions"   : [self.__shiftToSelectedClass],
                                                           "gui_state" : "show_tree"}
                                     },
            # "state"      : {"event": {"next_state": add next state,
            #                                                "actions"   : [list of actions],
            #                                                "gui_state" : specify gui shows (separate dictionary}
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
    self.current_class = self.root_class_container

  def __selectedItem(self, state, data):
    """
    data is a list with selected item ID, associated predicate and a graph ID
    """
    self.current_node = data[0]

  def __checkSelection(self, state, data):

    sub, p, o, graph_ID = data
    item_ID = o
    predicate = p
    graph = self.data_container[self.current_data_tree]
    container_graph = self.ContainerGraph

    is_data_class = graph.isClass(sub) or (not sub)
    is_container_class = container_graph.isClass(sub)
    # if is_data_class or is_container_class:
    #   self.current_class = sub

    is_sub_class = graph.isSubClass(sub, graph_ID)
    is_value = graph.isValue(predicate)
    is_integer = graph.isInteger(predicate)
    is_comment = graph.isComment(predicate)
    is_string = graph.isString(predicate)
    # is_linked = graph.isLinked(sub, graph_ID)
    is_linked = (predicate == "link_to_class")

    is_instantiated = graph.isInstantiated(item_ID)

    txt = "selection has data: %s    " % data

    if is_data_class: txt += " & class"
    if is_container_class: txt += " & container_class"
    if is_sub_class: txt += " & subclass"
    # if is_primitive: s += " & primitive"
    if is_value: txt += " & value"
    if is_linked: txt += " & is_linked"
    if is_instantiated: txt += " & instantiated"
    if is_integer: txt += " & integer"
    if is_comment: txt += " & comment"
    if is_string: txt += " & string"

    print("selection : %s\n" % txt)

    if is_data_class or is_sub_class:
      if is_instantiated:
        self.ui_state("has_ID")
      else:
        self.ui_state("has_no_ID")

    if is_linked:
      self.__shiftClass(sub, is_container_class)

  # def __makeTriple(self):
  #   triple = (self.current_node, "is_a", self.)

  # def __4_getAllIdentifiers(self, state, event_data):
  #   for g in self.RDFConjunctiveGraph:
  #     self.identifiers[g] = []
  #     for s, p, o in self.RDFConjunctiveGraph[g].triples((None, RDFSTerms["value"], None)):  # RDFSTerms["string"])):
  #       print("found", s, p, o)
  #       if "Identifier" in o:
  #         self.identifiers[g].append(str(s))
  #   pass

  # def __5_showDataTree(self, state, event_data):

  def __updateDataWithNewID(self, state, data):
    print("debugging -- new ID", state, data)

  def __updateTree(self, state, data):
    print("debugging -- selected ID", state, data)

  def __shiftToSelectedClass(self, state, data):
    print("debugging -- shift class", data)

    graph = self.data_container[self.current_data_tree]
    container_graph = self.ContainerGraph
    sub = data
    # is_data_class = graph.isClass(sub) or (not sub)
    is_container_class = container_graph.isClass(sub)
    self.__shiftClass(sub, is_container_class)

    pass

  def __shiftClass(self, class_ID, is_what):
    global class_path
    self.current_class = class_ID
    if class_ID not in class_path:
      # self.listClasses.append(class_ID)
      # self.FrontEnd.populate("selectors", "classList", self.listClasses)
      class_path.append(class_ID)
    else:
      i = class_path.index(class_ID)
      class_path = class_path[:i + 1]
      # self.FrontEnd.
      # self.clear()
      # self.ui.listClasses.addItems(class_path)
    pass

    self.__makeDataTree(class_ID, is_what)

    self.FrontEnd.controls("selectors", "classList", "populate", class_path)

  def __createDataTree(self, state, data):
    """
    data dictionary has two components:
    data_ID : enumerator
    root_class : root class of the added tree
    """
    global class_path

    if not self.data_container:
      data_ID = 1
      root_class = self.root_class_container
      data_root_class = self.__makeFirstDataRoot(root_class, data_ID)
      class_path = [data_root_class]
    else:
      if "data_ID" in data:
        data_ID = data["data_ID"]
        root_class = data["root_class"]
      else:
        data_ID = -1
        root_class = self.root_class_container

    self.current_data_tree = data_ID
    self.addGraphToDataGraph(data_ID, root_class)

  def addGraphToDataGraph(self, data_ID, container_root_class):
    self.data_container[data_ID]=  DataGraph()
    container_graph = self.ContainerGraph.RDFConjunctiveGraph[container_root_class]
    root_class = self.__makeFirstDataRoot(container_root_class, data_ID)
    self.data_container[data_ID].create(root_class)
    self.current_class = root_class
    for s, p, o in container_graph.triples((None, None, None)):
      if str(s) == container_root_class:
        s_ = Literal(root_class)
      else:
        s_ = s
      if str(o) == container_root_class:
        o_ = Literal(root_class)
      else:
        o_ = o
      data_graph = self.data_container[data_ID].RDFConjunctiveGraph[root_class]
      data_graph.add((s_, p, o_))
    pass
    self.data_container[1].makeAllLists()

  def __makeFirstDataRoot(self, container_root_class, data_ID):
    root_class = container_root_class + DELIMITERS["instantiated"] + str(data_ID)
    return root_class

  def __addToDataTree(self, state, data):
    data = 1

  def __makeDataTreeFromFile(self, state, file_name):
    self.__makeDataTree(state, False)

  def __makeDataTree(self, graph_ID, is_what):

    if not is_what:
      print("make it from data container")
      graph = self.data_container[self.current_data_tree].RDFConjunctiveGraph[self.current_class]
    else:
      print("make it from ontology container")
      graph = self.ContainerGraph.RDFConjunctiveGraph[self.current_class]

    self.quads = convertRDFintoInternalMultiGraph(graph, self.current_class)
    self.FrontEnd.controls("selectors", "classTree", "populate", self.quads, self.current_class) #str(graph.identifier))
    self.__makeClassList()

  # def __makeTree(self, state, data):
  #
  #
  #   # self.root_class = name
  #   # self.RDFConjunctiveGraph = {self.root_class: Graph('Memory', Literal(self.root_class))}
  #   # self.current_class = self.root_class
  #   # self.subclass_names[self.root_class] = [self.root_class]
  #   # self.class_names.append(self.root_class)
  #   # class_path = [self.root_class]
  #   # self.link_lists[self.root_class] = []
  #   # self.listClasses = [class_path]
  #   # # self.ui.listClasses.addItems(class_path)
  #   # self.class_definition_sequence.append(self.root_class)
  #   # self.primitives[self.root_class] = {self.root_class: []}
  #   # self.changed = True
  #
  #   graph = self.ContainerGraph.RDFConjunctiveGraph[self.current_class]
  #   self.quads = prepareTree(graph, "container")
  #   self.FrontEnd.controls("selectors", "classTree", "populate", self.quads, self.root_class_container)
  #   self.__makeClassList()

  def __makeClassList(self):
    path = self.data_container[self.current_data_tree].txt_class_path
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
    elif state == "NoSet":
      return

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
    elif state == "has_ID":
      show = {"buttons"  : ["save",
                            "exit",
                            "visualise",
                            "instantiate",
                            ],
              "selectors": ["classList",
                            "classTree"],
              }
    elif state == "has_no_ID":
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
            self.FrontEnd.controls(oc, o, "show")

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
  #     self.FrontEnd.controls("selectors", "classList", "populate", class_path)
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
