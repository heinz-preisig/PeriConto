"""
Backend to the construction of a data base for coatings formulations

The data are stored in triple stored in triple stores

rule: notation
an instantiated "node" is <<name>>:<<ID>>

"""
import copy

DELIMITERS = {"instantiated": ":",
              "path"        : "/"}

from rdflib import Graph
from rdflib import Literal

from PeriConto import MYTerms
from PeriConto import ONTOLOGY_DIRECTORY
from PeriConto import PRIMITIVES
from PeriConto import RDFSTerms
from PeriConto import VALUE
from PeriConto import getData
from PeriConto import makeRDFCompatible




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
    self.enumerators = {}

    self.RDFConjunctiveGraph = {}

  def create(self, root_class):
    self.txt_root_class = root_class
    self.RDFConjunctiveGraph = {self.txt_root_class: Graph('Memory', identifier=root_class)}
    self.txt_subclass_names[self.txt_root_class] = [self.txt_root_class]
    self.txt_class_names.append(self.txt_root_class)
    self.txt_class_path = [self.txt_root_class]
    self.txt_link_lists[self.txt_root_class] = []
    self.class_definition_sequence.append(self.txt_root_class)
    self.txt_primitives[self.txt_root_class] = {self.txt_root_class: []}
    self.enumerators[self.txt_root_class] = {self.txt_root_class: None}            # keeps track of instances

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

      for s, p, o in graphs_internal[g]:
        self.addGraphGivenInInternalNotation(s, p, o, g)

    self.makeAllListsForAllGraphs()

    return self.txt_root_class

  def makeAllListsForAllGraphs(self):
    print("debugging")
    for rdf_graph_ID in self.RDFConjunctiveGraph:
      rdf_graph = self.RDFConjunctiveGraph[rdf_graph_ID]
      self.makeAllListsForOneGraph(rdf_graph, rdf_graph_ID)
    pass

  def makeAllListsForOneGraph(self, rdf_graph, rdf_graph_ID):
    self.txt_subclass_names[rdf_graph_ID] = makeListBasedOnPredicates(rdf_graph, "is_a_subclass_of")
    self.txt_link_lists[rdf_graph_ID] = makeLinkListBasedOnPredicates(rdf_graph, rdf_graph_ID, "link_to_class")
    self.txt_value_lists[rdf_graph_ID] = makeListBasedOnPredicates(rdf_graph, "value")
    self.txt_integer_lists[rdf_graph_ID] = makeListBasedOnPredicates(rdf_graph, "integer")
    self.txt_string_lists[rdf_graph_ID] = makeListBasedOnPredicates(rdf_graph, "string")
    self.txt_comment_lists[rdf_graph_ID] = makeListBasedOnPredicates(rdf_graph, "comment")

  def addGraphGivenInInternalNotation(self, subject_internal, predicate_internal, object_internal, graph_ID):
    rdf_subject = makeRDFCompatible(subject_internal)
    rdf_object = makeRDFCompatible(object_internal)
    rdf_predicate = RDFSTerms[predicate_internal]
    self.RDFConjunctiveGraph[graph_ID].add((rdf_subject, rdf_predicate, rdf_object))

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

  # def isInstantiated(self, ID):
  #   return DELIMITERS["instantiated"] in ID


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


  def load(self, JsonFile):
    self.txt_root_class = super().load(JsonFile)
    for g in self.RDFConjunctiveGraph:
      self.enumerators[g] = {}
      for s, p, o in self.RDFConjunctiveGraph[g]:
        self.enumerators[str(g)][str(o)] = None                          # instantiate enumerators
    return self.txt_root_class


class DataGraph(SuperGraph):

  def __init__(self):
    SuperGraph.__init__(self)
    pass


class WorkingTree(SuperGraph):

  def __init__(self, container_graph):
    SuperGraph.__init__(self)
    self.container_graph = container_graph
    self.RDFConjunctiveGraph = copy.deepcopy(container_graph.RDFConjunctiveGraph)



  def instantiateAlongPath(self, path, no):

    # path_list = path.split(DELIMITERS["path"])
    for graphID in self.RDFConjunctiveGraph:
      graph = self.RDFConjunctiveGraph[graphID]
      for s, p, o in graph:
        if (str(s) in path) and (not isInstantiated(str(s))):
          s_ = makeID(s,no)
          triple = (Literal(s_), p, o)
          graph.remove((s,p,o))
          graph.add(triple)

      for s,p,o in graph:
        if (str(o) in path) and (not isInstantiated(str(o))):
          o_ = makeID(o,no)
          triple = (s, p, Literal(o_))
          graph.remove((s,p,o))
          graph.add(triple)

    instantiated_classes = {}
    for graphID in list(self.RDFConjunctiveGraph.keys()):
      if (graphID in path) and (not isInstantiated(graphID)):
        graphID_ = makeID(graphID,no)
        self.RDFConjunctiveGraph[graphID_] = self.RDFConjunctiveGraph[graphID]
        del self.RDFConjunctiveGraph[graphID]
        instantiated_classes[graphID] = graphID_

    return no, instantiated_classes


  def overlayContainerGraph(self, graph_ID, rdf_data_class_graph):
    print("debugging -- overlay container graph")
    self.graph_ID = graph_ID
    self.RDFConjunctiveGraph[graph_ID] = rdf_data_class_graph

    container_graph_ID, instance_ID = getID(graph_ID)
    container_class_graph = self.container_graph.RDFConjunctiveGraph[container_graph_ID]

    working_graph = Graph()

    if len(rdf_data_class_graph) == 0:
      for s, p, o in container_class_graph.triples((None, None, None)):
        if str(s) == container_graph_ID:
          s_ = Literal(graph_ID)
        else:
          s_ = s
        if str(o) == container_graph_ID:
          o_ = Literal(graph_ID)
        else:
          o_ = o
        working_graph.add((s_, p, o_))
    # else:
    #   for s, p, o in working_graph.triples((None, None, None)):
    #     print("- %s,  %s,  %s" % (s, p, o))

      for d_s, d_p, d_o in rdf_data_class_graph.triples((None, None, None)):
        # print(">>> %s, %s, %s" % (d_s, d_p, d_o))
        for s, p, o in container_class_graph.triples((None, None, None)):
          _s, no_s = getID(str(s))
          _o, no_o = getID(str(o))
          t_s = Literal(_s)
          t_o = Literal(_o)
          l_s = (t_s == d_s)
          l_p = (p == d_p)
          l_o = (t_o == d_o)
          if l_s and l_p and l_o:
            working_graph.add((s, p, o))
          elif l_s and l_p:
            working_graph.add((t_s, p, d_o))
          elif l_o and l_p:
            working_graph.add((d_s, p, t_o))
          else:
            working_graph.add((s, p, o))

    # for s, p, o in working_graph.triples((None, None, None)):
    #   print("- %s,  %s,  %s" % (s, p, o))
    return working_graph

def isInstantiated(ID):
  id = str(ID)
  # print("debugging ==", id,(DELIMITERS["instantiated"] in id))
  return DELIMITERS["instantiated"] in id

def getID(ID):
  container_graph_ID, instance_ID = ID.split(DELIMITERS["instantiated"])
  return container_graph_ID, instance_ID


def makeID(ID, no):
  return ID + DELIMITERS["instantiated"] + str(no)

class Enumerator(int):
  def __init__(self):
    self = 0

  def newValue(self):
    self += 1
    return self

class BackEnd:

  def __init__(self, FrontEnd):

    global state
    global class_path
    global data_container_number
    global data_container
    global working_tree

    self.FrontEnd = FrontEnd
    self.changed = False

    self.ContainerGraph = ContainerGraph()
    data_container = {}

    self.ui_state("start")
    self.event_data = None
    self.current_node = None
    self.current_class = None
    self.current_subclass = None
    data_container_number = 0
    class_path = []

    self.instanceEnumerator = Enumerator()

    data_container = {}

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
                                                                    self.__makeWorkingTree,
                                                                    self.__shiftClass,
                                                                    ],
                                                     "gui_state" : "show_tree"},
                                       },
            "show_tree"             : {"selected": {"next_state": "check_selection",
                                                    "actions"   : [self.__selectedItem,
                                                                   ],
                                                    "gui_state" : "NoSet"},
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
            "class_list_clicked"    : {"selected": {"next_state": "show_tree",
                                                    "actions"   : [self.__shiftToSelectedClass],
                                                    "gui_state" : "show_tree"}
                                       },
            # "state"      : {"event": {"next_state": add next state,
            #                                                "actions"   : [list of actions],
            #                                                "gui_state" : specify gui shows (separate dictionary}
            #                          },
            }
    pass

  def processEvent(self, state, Event, event_data):
    # Note: cannot be called from within backend -- generates new name space
    global gui_state
    global current_event_data
    global automaton_next_state
    global action
    global data_container_number
    global data_container

    current_event_data = event_data

    if state not in self.automaton:
      print("stopping here - no such state", state)
      return
    if Event not in self.automaton[state]:
      print("stopping here - no such event", Event, "  at state", state)
      return

    next_state = self.automaton[state][Event]["next_state"]
    actions = self.automaton[state][Event]["actions"]
    gui_state = self.automaton[state][Event]["gui_state"]

    automaton_next_state = next_state

    print("automaton -- ",
          "\n             state   :", state,
          "\n             next    :", next_state,
          "\n             actions :", actions,
          "\n             gui     :", gui_state,
          "\n             data    :", event_data,
          "\n")

    for action in actions:
      if action:
        action()
    self.ui_state(gui_state)

    return next_state

  def __0_askForFileName(self):
    global current_event_data
    global automaton_next_state

    state = automaton_next_state

    self.FrontEnd.fileNameDialog(state, "file_name",
                                 "ontology",
                                 ONTOLOGY_DIRECTORY,
                                 "*.json",
                                 "exit")

  def __1_loadOntology(self):
    global current_event_data
    global working_tree

    event_data = current_event_data
    self.root_class_container = self.ContainerGraph.load(event_data)
    working_tree = WorkingTree(self.ContainerGraph)
    self.current_class = self.root_class_container

  def __selectedItem(self):
    #   """
    #   data is a list with selected item ID, associated predicate and a graph ID
    #   """
    global current_event_data
    global automaton_next_state
    global data_container_number
    global working_tree
    global is_container_class

    self.current_node = current_event_data[0]
    sub, p, o, graph_ID, path = current_event_data
    item_ID = o
    predicate = p

    is_data_class = working_tree.isClass(sub) or (not sub)
    is_container_class = self.ContainerGraph.isClass(sub)

    is_sub_class = working_tree.isSubClass(sub, graph_ID)
    is_value = working_tree.isValue(predicate)
    is_integer = working_tree.isInteger(predicate)
    is_comment = working_tree.isComment(predicate)
    is_string = working_tree.isString(predicate)
    is_linked = (predicate == "link_to_class")

    is_instantiated = isInstantiated(item_ID)

    txt = "selection has data: %s    " % current_event_data

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
      print("shifting event data :", current_event_data)
      self.current_class = sub
      self.__makeWorkingTree()
      self.__shiftClass()

  def __updateDataWithNewID(self):
    global current_event_data
    global automaton_next_state
    global working_tree
    global class_path

    print("debugging new ID : event data -- ", current_event_data)
    print("debugging new ID : current class", self.current_class)
    s,p,o = current_event_data["triple"]
    if isInstantiated(s):
      return


    no = self.instanceEnumerator.newValue()

    path = current_event_data["path"]
    instance_no, instantiated_classes = working_tree.instantiateAlongPath(path, no)

    # fix class_list:
    for i in class_path:
      if i in instantiated_classes:
        index = class_path.index(i)
        class_path[index]= instantiated_classes[i]

    if not isInstantiated(self.current_class):
      self.current_class = makeID(self.current_class, instance_no)

    print("debugging", class_path)

    self.__makeWorkingTree()
    self.FrontEnd.controls("selectors", "classTree", "populate", self.quads, self.current_class)
    self.FrontEnd.controls("selectors", "classList", "populate", class_path)



  def __updateTree(self):  # , state, data):
    global current_event_data
    global automaton_next_state
    print(">>>", current_event_data, automaton_next_state)

  def __shiftToSelectedClass(self):  # , state, data):
    global current_event_data

    print("shifting event data :", current_event_data)

    self.current_class = current_event_data
    self.__makeWorkingTree()
    self.__shiftClass()

  def __shiftClass(self):
    global class_path

    # self.current_class = class_ID
    class_ID = self.current_class
    if class_ID not in class_path:
      class_path.append(class_ID)
    else:
      i = class_path.index(class_ID)
      class_path = class_path[:i + 1]
    pass

    self.FrontEnd.controls("selectors", "classTree", "populate", self.quads, self.current_class)
    self.FrontEnd.controls("selectors", "classList", "populate", class_path)

    # def __createDataTree(self):  # , state, data):
    #   """
    #   data dictionary has two components:
    #   data_ID : enumerator
    #   root_class : root class of the added tree
    #   """
    #   global class_path
    #   global current_event_data
    #   global automaton_next_state
    #   global data_container_number
    #   global data_container
    #
    #   data_container_number = 1
    #
    #   data_container[data_container_number] = DataGraph()
    #   self.__makeDataTree()

    print(">>>", current_event_data, automaton_next_state)

    # data = current_event_data
    #
    # if not self.data_container:
    #   data_ID = 1
    #   root_class = self.root_class_container
    #   data_root_class = self.__makeFirstDataRoot(root_class, data_ID)
    #   class_path = [data_root_class]
    # else:
    #   if "data_ID" in data:
    #     data_ID = data["data_ID"]
    #     root_class = data["root_class"]
    #   else:
    #     data_ID = -1
    #     root_class = self.root_class_container
    #
    # self.current_data_tree = data_ID
    # working_tree = WorkingGraph(self.ContainerGraph)
    # self.data_container[data_ID] = DataGraph()
    # data_root_class = self.__makeFirstDataRoot(root_class, data_ID)
    # self.data_container[data_ID].create(data_root_class)
    # self.current_working_tree = working_tree.overlayContainerGraph(
    #         data_root_class,
    #         self.data_container[data_ID].RDFConjunctiveGraph[data_root_class])
    # self.current_class = data_root_class
    pass

    # self.addGraphToDataGraph(data_ID, root_class)

  # def addGraphToDataGraph(self, data_ID, container_root_class):
  #   self.data_container[data_ID] = DataGraph()
  #   container_graph = self.ContainerGraph.RDFConjunctiveGraph[container_root_class]
  #   root_class = self.__makeFirstDataRoot(container_root_class, data_ID)
  #   self.data_container[data_ID].create(root_class)
  #   self.current_class = root_class
  #   for s, p, o in container_graph.triples((None, None, None)):
  #     if str(s) == container_root_class:
  #       s_ = Literal(root_class)
  #     else:
  #       s_ = s
  #     if str(o) == container_root_class:
  #       o_ = Literal(root_class)
  #     else:
  #       o_ = o
  #     data_graph = self.data_container[data_ID].RDFConjunctiveGraph[root_class]
  #     data_graph.add((s_, p, o_))
  #   pass
  #   self.data_container[1].makeAllLists()

  def __makeFirstDataRoot(self, container_root_class, data_ID):
    global data_container_number

    root_class = container_root_class + DELIMITERS["instantiated"] + str(data_ID)
    return root_class

  # def __addToDataTree(self, state, data):
  #   data = 1

  # def __makeDataTreeFromFile(self):  # , state, file_name):
  #   global current_event_data
  #   global automaton_next_state
  #   print(">>>", current_event_data, automaton_next_state)
  #   state = automaton_next_state
  #   self.__makeDataTree() #state, False)

  def __makeWorkingTree(self):
    global data_container_number
    global data_container
    global working_tree
    global is_container_class
    print("debugging make tree")

    if (data_container_number == 0) or is_container_class:
      working_tree.makeAllListsForAllGraphs()
    else:
      data_root_class = self.__makeFirstDataRoot(root_class, data_container_number)
      data_container[data_container_number].create(data_root_class)
      self.current_working_tree = working_tree.overlayContainerGraph(
              data_root_class,
              data_container[data_container_number].RDFConjunctiveGraph[data_root_class])

    self.quads = convertRDFintoInternalMultiGraph(working_tree.RDFConjunctiveGraph[self.current_class],
                                                  self.current_class)

    # self.quads = convertRDFintoInternalMultiGraph(working_tree.RDFConjunctiveGraph[self.current_class], self.current_class)
    #
    # self.FrontEnd.controls("selectors", "classTree", "populate", self.quads, self.current_class)
    # self.__makeClassList()

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

  # def __makeClassList(self):
  #   global data_container_number
  #
  #   if data_container_number == 0:
  #     path = [self.current_class]
  #   else:
  #     path = data_container[data_container_number].txt_class_path
  #   self.FrontEnd.controls("selectors", "classList", "populate", path)
  #   pass

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
