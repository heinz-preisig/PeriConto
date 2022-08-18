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
from PeriConto import plot

def copyRDFGraph(G_original):
  G_copy = Graph()
  for triple in G_original:
    G_copy.add(triple)
  return G_copy


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


#
# def makeDotGraph(RDF_rdf_graph_dictionary, root_name, class_names):
#     graph_overall = Graph()
#     for cl in RDF_rdf_graph_dictionary:
#       for t in RDF_rdf_graph_dictionary[cl].triples((None, None, None)):
#         graph_overall.add(t)
#     dot = plot(graph_overall, class_names)
#     # print("debugging -- dot")
#     graph_name = self.root_class
#     dot.render(graph_name, directory=ONTOLOGY_DIRECTORY)
#     return dot

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
    # self.enumerators[self.txt_root_class] = {self.txt_root_class: None}  # keeps track of instances

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
    #
    # for g in list(self.RDFConjunctiveGraph.keys()):
    #   print("\n >> loaded graph %s" % g)
    #   for s, p, o in self.RDFConjunctiveGraph[g].triples((None,None,None)):
    #     print("- ", str(s), MYTerms[p], str(o))

    return self.txt_root_class

  def makeAllListsForAllGraphs(self):
    # print("debugging")
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

  def makeDotGraph(self):
    graph_overall = Graph()
    for cl in self.RDFConjunctiveGraph:
      for t in self.RDFConjunctiveGraph[cl].triples((None, None, None)):
        graph_overall.add(t)
    dot = plot(graph_overall, self.txt_class_names)
    # print("debugging -- dot")
    graph_name = self.txt_root_class
    dot.render(graph_name, directory=ONTOLOGY_DIRECTORY)
    return dot

  def printMe(self, text):


    for g in list(self.RDFConjunctiveGraph.keys()):
      print("\n %s %s" % (text, g))
      for s, p, o in self.RDFConjunctiveGraph[g].triples((None,None,None)):
        print("- ", str(s), MYTerms[p], str(o))

    # for c in self.RDFConjunctiveGraph:
    #   for s,p,o in self.RDFConjunctiveGraph[c]:
    #     print(c, str(s), MYTerms[p], str(s))

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
    self.enumerators = {"classes"         : {},
                        "nodes_in_classes": {}}
    pass

  def load(self, JsonFile):
    self.txt_root_class = super().load(JsonFile)
    for class_ID in self.RDFConjunctiveGraph:
      self.enumerators["classes"][class_ID] = -1
      self.enumerators["nodes_in_classes"][class_ID] = {}
      for s, p, o in self.RDFConjunctiveGraph[class_ID]:
        self.enumerators["nodes_in_classes"][class_ID][str(o)] = -1  # instantiate enumerators
        self.enumerators["nodes_in_classes"][class_ID][str(s)] = -1  # instantiate enumerators
    return self.txt_root_class

  def incrementClassEnumberator(self, class_ID):
    v = self.enumerators["classes"][class_ID]
    v += 1
    return v

  def incrementNodeEnumerator(self, class_ID, node_ID):
    v = self.enumerators["nodes_in_classes"][class_ID][node_ID]
    v += 1
    return v

  # def getEnumerator(self, graph_ID, subject):
  #   if isInstantiated(graph_ID):
  #     ID, no = getID(graph_ID)
  #   else:
  #     ID = graph_ID
  #   if isInstantiated(subject):
  #     sub, no = getID(subject)
  #   else:
  #     sub = subject
  #
  #   return self.enumerators[ID][sub]


class DataGraph(SuperGraph):

  def __init__(self):
    SuperGraph.__init__(self)
    pass


class WorkingTree(SuperGraph):

  def __init__(self, container_graph):
    SuperGraph.__init__(self)
    self.container_graph = container_graph

    ### oops does not work!
    # self.RDFConjunctiveGraph = copy.deepcopy(container_graph.RDFConjunctiveGraph)
    self.RDFConjunctiveGraph = {}
    for c in container_graph.RDFConjunctiveGraph:
      G_original = container_graph.RDFConjunctiveGraph[c]
      self.RDFConjunctiveGraph[c]= copyRDFGraph(G_original)


    # self.printMe("copied into the working tree")


  def instantiateAlongPath(self, paths_in_classes, class_path, reminder):

    # print("debugging -- class path and paths in classes", class_path, paths_in_classes)
    # for c in reversed(class_path):
    for c_no in range(len(class_path)-1,-1,-1):
      c = class_path[c_no]
      print(">>>>>>>>>>>> ", c)
      nodes = paths_in_classes[c].split(DELIMITERS["path"])
      N = nodes[-1]
      from_graph = copy.deepcopy(self.RDFConjunctiveGraph[c])
      updated_nodes = []
      instantiated = {}
      for node_no in reversed(range(1, len(nodes))):
        # print(nodes[node_no], nodes[node_no - 1])
        for s, p, o in from_graph.triples((Literal(nodes[node_no]), None, Literal(nodes[node_no - 1]))):
          ss = str(s)
          os = str(o)
          s_original = getID(ss)
          o_original = getID(os)
          c_original = getID(c)
          # print(ss, MYTerms[p], os)
          if (not isInstantiated(ss)) and (not isInstantiated((os))):
            enum = self.container_graph.incrementNodeEnumerator(c_original, s_original)
            s_i = makeID(s, enum)
            enum = self.container_graph.incrementNodeEnumerator(c_original, o_original)
            o_i = makeID(o, enum)
            from_graph.remove((s, p, o))
            from_graph.add((s_i, p, o_i))
            if str(s_i) not in updated_nodes:
              updated_nodes.append(str(s_i))
            if str(o_i) not in updated_nodes:
              updated_nodes.append(str(o_i))
              instantiated[ss] = str(s_i)
              instantiated[os] = str(o_i)
          elif (not isInstantiated(ss)):
            enum = self.container_graph.incrementNodeEnumerator(c_original, s_original)
            s_i = makeID(s, enum)
            from_graph.remove((s, p, o))
            from_graph.add((Literal(s_i), p, o))
            if str(s_i) not in updated_nodes:
              updated_nodes.append(str(s_i))
            instantiated[ss] = str(s_i)
        for s,p,o in from_graph.triples((None, RDFSTerms["is_a_subclass_of"], None)):
          if (not isInstantiated(str(s))) \
                  and (not isInstantiated(str(o))) \
                  and ( str(o) in instantiated):
            o_i = instantiated[str(o)]
            from_graph.add((s,p,Literal(o_i)))
            from_graph.remove((s,p,o))

        # fix links
        links = []
        print("\n==== c")
        for s,p,o in from_graph.triples((None, RDFSTerms["link_to_class"], None)):
          print("found ", str(s), MYTerms[p], str(o))
          link_node = paths_in_classes[c].split(DELIMITERS["path"])[-1]
          s_original = getID(str(s))
          o_original = getID(str(o))
          cc = class_path[c_no+1]
          enum = getIDNo(str(cc))
          if (link_node == str(o)) :
            print("got here", s,MYTerms[p],o)
            s_i = makeID(s_original, enum)
            links.append(((s,p,o), (Literal(s_i),p,o)))

        for (t_old, t_new) in links:
          from_graph.add(t_new)
          from_graph.remove(t_old)
          s,p,o = t_old
          print("debugging -- old", str(s), MYTerms[p], str(o))
          s,p,o = t_new
          print("debugging -- new", str(s), MYTerms[p], str(o))


      # for u in instantiated:
      #   if u in nodes:
      #     i = nodes.index(u)
      #     nodes[i] = instantiated[u]

      # print("debugging updated nodes", nodes)

      # print("==========")
      # for s, p, o in from_graph:
      #   print(s, MYTerms[p], o)

      c_store = c
      if c in instantiated:
        node_no = self.container_graph.incrementClassEnumberator(c)
        c_i = makeID(c, node_no)
        path = DELIMITERS["path"].join(reversed(updated_nodes))
        paths_in_classes[c_i] = path
        del paths_in_classes[c]
        index = class_path.index(c)
        class_path[index] = c_i
        c_store = c_i
        del self.RDFConjunctiveGraph[c]

      self.RDFConjunctiveGraph[c_store]=  from_graph




      # print("updated class path", class_path)
      # print("updated paths in classes", paths_in_classes)
      #
      # print("==========")
    return  class_path, paths_in_classes




  def overlayContainerGraph(self, graph_ID, rdf_data_class_graph):
    # print("debugging -- overlay container graph")
    self.graph_ID = graph_ID
    self.RDFConjunctiveGraph[graph_ID] = rdf_data_class_graph

    container_graph_ID = getID(graph_ID)
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
          _s = getID(str(s))
          _o = getID(str(o))
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
  if DELIMITERS["instantiated"] in ID:
    container_graph_ID, instance_ID = ID.split(DELIMITERS["instantiated"])
  else:
    container_graph_ID = ID
    instance_ID = None
  return container_graph_ID

def getIDNo(ID):
  if DELIMITERS["instantiated"] in ID:
    container_graph_ID, instance_ID = ID.split(DELIMITERS["instantiated"])
  else:
    container_graph_ID = ID
    instance_ID = None
  return instance_ID

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
    # global working_tree

    self.FrontEnd = FrontEnd
    self.changed = False

    self.ContainerGraph = ContainerGraph()
    data_container = {}
    self.working_tree = None

    self.ui_state("start")
    self.current_node = None
    self.current_class = None
    # self.previous_class = None
    self.current_subclass = None
    data_container_number = 0
    class_path = []

    self.path_at_transition = {}  # Note: path at the point of transition to another class. Key: class_ID

    self.instanceEnumerator = Enumerator()

    self.automaton = {
            "start"                 : {"initialise": {"next_state": "initialised",
                                                      "actions"   : [None],
                                                      "gui_state" : "start"},
                                       },
            "initialised"           : {"create": {"next_state": "got_ontology_file_name",
                                                  "actions"   : [self.__askForFileName],
                                                  "gui_state" : "initialise"},
                                       },
            "got_ontology_file_name": {"file_name": {"next_state": "show_tree",
                                                     "actions"   : [self.__loadOntology,
                                                                    self.__makeWorkingTree,
                                                                    self.__shiftClass,
                                                                    ],
                                                     "gui_state" : "show_tree"},
                                       },
            "show_tree"             : {"selected": {"next_state": "check_selection",
                                                    "actions"   : [self.__processSelectedItem,
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
            "visualise"             : {"dot_plot": {"next_state": "show_tree",
                                                    "actions"   : [self.__makeDotPlot],
                                                    "gui_state" : "show_tree"}
                                       },
            # "state"      : {"event": {"next_state": add next state,
            #                                                "actions"   : [list of actions],
            #                                                "gui_state" : specify gui shows (separate dictionary}
            #                          },
            }
    pass

  def __askForFileName(self):
    global current_event_data
    global automaton_next_state

    state = automaton_next_state

    self.FrontEnd.fileNameDialog(state, "file_name",
                                 "ontology",
                                 ONTOLOGY_DIRECTORY,
                                 "*.json",
                                 "exit")

  def __loadOntology(self):
    global current_event_data
    # global working_tree

    file_name = current_event_data["file_name"]

    event_data = current_event_data
    self.root_class_container = self.ContainerGraph.load(file_name)

    self.ContainerGraph.printMe("loaded")

    self.working_tree = WorkingTree(self.ContainerGraph)
    self.current_class = self.root_class_container

  def __processSelectedItem(self):
    #   """
    #   data is a list with selected item ID, associated predicate and a graph ID
    #   """
    global current_event_data
    global automaton_next_state
    global data_container_number
    # global working_tree
    global is_container_class

    subject, predicate, obj = current_event_data["triple"]
    graph_ID = current_event_data["class"]
    path = current_event_data["path"]

    self.current_node = subject

    is_data_class = self.working_tree.isClass(subject) or (not subject)
    is_container_class = self.ContainerGraph.isClass(subject)
    is_sub_class = self.working_tree.isSubClass(subject, graph_ID)
    is_value = self.working_tree.isValue(predicate)
    is_integer = self.working_tree.isInteger(predicate)
    is_comment = self.working_tree.isComment(predicate)
    is_string = self.working_tree.isString(predicate)
    is_linked = (predicate == "link_to_class")
    is_instantiated = isInstantiated(obj)

    debugging = True
    if debugging:
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
      # print("selection : %s\n" % txt)

    if is_data_class or is_sub_class:
      if is_instantiated:
        self.ui_state("has_ID")
      else:
        self.ui_state("has_no_ID")

    if is_linked:
      # print("shifting event data :", current_event_data)
      # self.previous_class = self.current_class
      self.current_class = subject
      self.__makeWorkingTree()
      self.__shiftClass()

  def __updateDataWithNewID(self):
    global current_event_data
    global automaton_next_state
    # global working_tree
    global class_path

    subject, predicate, obj = current_event_data["triple"]
    path = current_event_data["path"]

    global_path = ""
    for t in class_path:
      if t == self.current_class:
        break
      # if isInstantiated(t) :
      #   t_, no_ = getID(t)
      # else:
      #   t_ = t
      try:
        global_path += self.path_at_transition[t]  # TODO: used?
      except:
        print("debugging -- got in trouble")

    global_path += path

    # print("debugging new ID : global path -- ", global_path)
    # print("debugging new ID : current class:", self.current_class)
    # print("debugging new ID : enumerators:", self.ContainerGraph.enumerators)
    # print("debugging new ID : subject:", subject)
    # print("debugging new ID : event data -- ", current_event_data)

    # if isInstantiated(subject):
    #   print(">>> instantiate -- %s is already instantiated" % subject)
    #   return

    # no = self.ContainerGraph.getEnumerator(self.current_class, subject) + 1

    paths_in_classes = self.path_at_transition
    paths_in_classes[self.current_class] = path

    # instance_no, instantiated_classes = working_tree.instantiateAlongPath(global_path, no)


    # self.working_tree.printMe("before instantiate")
    class_path, paths_in_classes = self.working_tree.instantiateAlongPath(paths_in_classes,
                                                                     class_path,
                                                                     len(class_path)
                                                                     )

    self.working_tree.printMe("after instantiate")

    #  fix class_list:
    # for i in class_path:
    #   if i in instantiated_classes:
    #     index = class_path.index(i)
    #     class_path[index] = instantiated_classes[i]

    current_event_data = {"class": class_path[-1]}
    self.__shiftToSelectedClass()

    #
    # if not isInstantiated(self.current_class):
    #   self.current_class = makeID(self.current_class, instance_no)
    #
    # print("debugging", class_path)
    #
    # self.__makeWorkingTree()
    # self.FrontEnd.controls("selectors", "classTree", "populate", self.quads, self.current_class)
    # self.FrontEnd.controls("selectors", "classList", "populate", class_path)

  def __makeDotPlot(self):
    # global working_tree
    self.working_tree.makeDotGraph()

  def __updateTree(self):  # , state, data):
    global current_event_data
    global automaton_next_state
    # print(">>>", current_event_data, automaton_next_state)

  def __shiftToSelectedClass(self):  # , state, data):
    global current_event_data

    # print("shifting event data :", current_event_data)

    # self.previous_class = self.current_class
    self.current_class = current_event_data["class"]

    self.__makeWorkingTree()
    self.__shiftClass()

  def __shiftClass(self):
    global class_path
    global current_event_data

    if "path" in current_event_data:
      transition_path = "/".join(current_event_data["path"].split(DELIMITERS["path"])[:-1]) + DELIMITERS["path"]
      previous_class = class_path[-1:][0]
      self.path_at_transition[previous_class] = transition_path
      # print("debugging -- transition -- ", previous_class, self.current_class, self.path_at_transition)
    else:
      print("debugging -- no current path defined")

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

    # print(">>>", current_event_data, automaton_next_state)

  def __makeFirstDataRoot(self, container_root_class, data_ID):
    global data_container_number

    root_class = container_root_class + DELIMITERS["instantiated"] + str(data_ID)
    return root_class

  def __makeWorkingTree(self):
    global data_container_number
    global data_container
    # global working_tree
    global is_container_class
    # print("debugging make tree")

    if (data_container_number == 0) or is_container_class:
      self.working_tree.makeAllListsForAllGraphs()
    self.quads = convertRDFintoInternalMultiGraph(self.working_tree.RDFConjunctiveGraph[self.current_class],
                                                  self.current_class)

  def processEvent(self, state, Event, event_data):
    # Note: cannot be called from within backend -- generates new name space
    global gui_state
    global current_event_data
    global automaton_next_state
    global action
    global data_container_number
    global data_container

    show_automaton = False

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

    if show_automaton:
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
      # print("ooops -- no such gui state", state)

    # print("debugging -- state & show", state, show)

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
