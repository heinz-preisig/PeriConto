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

from graphviz import Digraph

from PeriConto import MYTerms
from PeriConto import ONTOLOGY_DIRECTORY
from PeriConto import PRIMITIVES
from PeriConto import RDFSTerms
from PeriConto import VALUE
from PeriConto import getData
from PeriConto import makeRDFCompatible
from PeriConto import DIRECTION


def copyRDFGraph(G_original):
  G_copy = Graph()
  for triple in G_original:
    G_copy.add(triple)
  return G_copy


def plot(graph, class_names=[]):
  """
  Create Digraph plot
  """
  dot = Digraph()
  # Add nodes 1 and 2
  suffix = 0
  for s, p, o in graph.triples((None, None, None)):
    ss = str(s)
    ss_ = str(ss).replace(":", "-")
    sp = str(p)
    so = str(o)
    so_ = str(o).replace(":", "-")
    s_ID = getID(str(s))
    if s_ID in PRIMITIVES:      # primitives are not having a unique name so we equip them with an incremental suffix
      if isInstantiated(ss):
        ss_ += "_%s" % suffix
        suffix += 1
    o_ID = getID(str(o))
    if o_ID in PRIMITIVES:
      if isInstantiated(so):
        so_ += "_%s" % suffix
        suffix += 1
    if ss in class_names:
      dot.node(ss_, color='red', shape="rectangle")
    elif so in PRIMITIVES:
      dot.node(so_, color='green', shape="rectangle")
    else:
      dot.node(ss_)

    if so in class_names:
      dot.node(so_, color='red', shape="rectangle")
    else:
      dot.node(so_)

    my_p = MYTerms[p]
    if DIRECTION[my_p] == 1:
      dot.edge(ss_, so_, label=my_p, color="blue")
    else:
      dot.edge(ss_, so_, label=my_p, color="green")

  # Visualize the graph
  return dot


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

def convertQuadsGraphIntoRDFGraph(quads):
  graph = Graph()
  for f,s,p,graphID in quads:
    if p not in ["value"] + PRIMITIVES:
      graph.add((Literal(f),RDFSTerms[p],Literal(s)))
    else:
      graph.add((Literal(s),RDFSTerms(p),Literal(f)))
  return graph

def extractSubTree(quads, root, extracts=[], stack=[]):
  for s,o,p,graphID in quads:
    if o == root:
      extracts.append((s,o,p,graphID))
      stack.append(s)
      extractSubTree(quads, s, extracts = extracts, stack=stack)




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


    pass


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

  def extractSubgraph(self, root, graph_ID):
    """
    extract an RDF-subgraph from an RDF-Graph given a root as a string, a label
    it is done via the quads generation that ignore the directionality
    """
    quads = convertRDFintoInternalMultiGraph(self.RDFConjunctiveGraph[graph_ID],graph_ID)
    extracts = []
    extractSubTree(quads, root, extracts)  # as quads
    graph = convertQuadsGraphIntoRDFGraph(extracts)
    return graph



  def printMe(self, text):

    for g in list(self.RDFConjunctiveGraph.keys()):
      print("\n %s %s" % (text, g))
      for s, p, o in self.RDFConjunctiveGraph[g].triples((None, None, None)):
        print("- ", str(s), MYTerms[p], str(o))

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
    return (predicate == "string")

  def isLinked(self, ID, graph_class):
    # graph_class is the currently active class
    for cl in self.txt_link_lists:
      for linked_class, linked_to_class, linked_to_subclass in self.txt_link_lists[cl]:
        if linked_to_class == graph_class:
          if linked_to_subclass == ID:
            return True


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
    for p in PRIMITIVES:
      self.enumerators[p] = -1

    return self.txt_root_class

  def incrementClassEnumberator(self, class_ID):
    v = self.enumerators["classes"][class_ID]
    v += 1
    self.enumerators["classes"][class_ID] = v
    return v

  def incrementNodeEnumerator(self, class_ID, node_ID):
    if node_ID == "b":
      print("debugging -- enumerator")
    v = self.enumerators["nodes_in_classes"][class_ID][node_ID]
    v += 1
    self.enumerators["nodes_in_classes"][class_ID][node_ID] = v
    return v

  def incrementPrimitiveEnumerator(self, primitive):
    v = self.enumerators[primitive]
    v += 1
    self.enumerators[primitive] = v
    return v

  # def extractSubgraph(self, relative_rdf_root):
  #
  #   graph = Graph()
  #   for c in self.RDFConjunctiveGraph:
  #     rdfGraph = self.RDFConjunctiveGraph[c]
  #     for s,p,o in rdfGraph:
  #       if o == relative_rdf_root:
  #         pass


class DataGraph(SuperGraph):

  def __init__(self):
    SuperGraph.__init__(self)
    pass


class Data(dict):
  def __init__(self):
    dict.__init__(self)
    self.enum = 0
    self.integers = {}
    self.strings = {}

  def addInteger(self, path, IDs, value):
    path_enum = self.addPath(path)
    key = (path_enum, IDs)
    print("debugging -- integer add key", key)
    if key not in self.integers:
      self.integers[key] = value
    else:
      print("adding integer >>> error")

  def addString(self, string, path):
    enum = self.addPath(path)
    if enum not in self.strings:
      self.strings[enum] = [string]
    else:
      self.strings[enum].append(string)

  def addPath(self, path):
    for p in self.values():
      if p == path:
        enum = self.getEnumerator(path)
        print("Data: path already exists", enum, p)
        return enum

    self.enum += 1
    self[self.enum] = path
    return self.enum

  def getPath(self, enum):
    if enum in self:
      return self[enum]
    else:
      return None

  def getEnumerator(self, path):
    for enum in self:
      if self[enum] == path:
        return enum

    return None


class WorkingTree(SuperGraph):

  def __init__(self, container_graph):
    SuperGraph.__init__(self)
    self.container_graph = container_graph

    self.data = Data()

    ### oops does not work!
    # self.RDFConjunctiveGraph = copy.deepcopy(container_graph.RDFConjunctiveGraph)
    self.RDFConjunctiveGraph = {}
    for c in container_graph.RDFConjunctiveGraph:
      G_original = container_graph.RDFConjunctiveGraph[c]
      self.RDFConjunctiveGraph[c] = copyRDFGraph(G_original)

    # self.container_graph.instantiateEnumerators()
    # self.printMe("copied into the working tree")

  def instantiateAlongPath(self, paths_in_classes, class_path):

    # print("debugging -- class path and paths in classes", class_path, paths_in_classes)
    # for c in reversed(class_path):

    instantiated = {}  # OrderedDict()

    c = class_path[-1]
    c_original = getID(c)
    from_graph = copy.deepcopy(self.RDFConjunctiveGraph[c])
    # print("debugging -- >>>>>>>>>>>> ", class_path, c)
    nodes = paths_in_classes[c].split(DELIMITERS["path"])

    instantiated[c_original] = {}

    if nodes[-1] not in PRIMITIVES:  # the last in the path must be a primitive being instantiated
      print("problems")

    ss = nodes[-2]
    os = nodes[-1]
    # print("debugging -- we have now subject and object, where the object is the data type", ss, os)
    rms_subject = Literal(nodes[-2])  # that's the one 'assigned' to the primitive
    rms_object = Literal(nodes[-1])  # that's the primitive
    s_original = nodes[-2]
    o_original = nodes[-1]  # that's the primitive
    # for primitive in PRIMITIVES:
    primitive = o_original
    # for s, p, o in from_graph.triples((rms_subject, RDFSTerms[primitive], rms_object)):
    last_s = None
    last_s_i = None

    for s, p, o in from_graph.triples((rms_subject, RDFSTerms[primitive], rms_object)):
      # print("debugging -- processing", str(s), MYTerms[p], str(o))
      if (isInstantiated(ss)):
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> error should not be instantiated")
      s_enum = self.container_graph.incrementNodeEnumerator(c_original, s_original)
      if o_original in PRIMITIVES:
        o_enum = self.container_graph.incrementPrimitiveEnumerator(primitive)
      else:
        o_enum = self.container_graph.incrementNodeEnumerator(c_original, o_original)
      s_i = makeID(ss, s_enum)
      instantiated[c_original][s_original] = s_i
      o_i = makeID(os, o_enum)
      instantiated[c_original][o_original] = o_i
      from_graph.remove((s, p, o))
      from_graph.add((Literal(s_i), p, Literal(o_i)))

      last_s = s
      last_s_i = s_i

    for s, p, o in from_graph.triples((None, RDFSTerms["value"], Literal(last_s))):

      if isInstantiated(str(s)):
        print(">>>>>>>>>>>>> problems")

      # print("debugging -- remove", str(s), MYTerms[p], str(o))
      s_original = getID(str(s))
      s_enum = self.container_graph.incrementNodeEnumerator(c_original, s_original)
      s_i = makeID(s_original, s_enum)
      instantiated[c_original][s_original] = s_i
      # print("debugging -- add", s_i, MYTerms[p], last_s_i)
      from_graph.remove((s, p, o))
      from_graph.add((Literal(s_i), p, Literal(last_s_i)))

    for n in reversed(nodes[:-2]):
      # print("debugging -- node", n)
      if n in instantiated[c_original]:
        # print("debugging -- instantiated ", n, instantiated[c_original][n])
        for s, p, o in from_graph.triples((Literal(n), RDFSTerms["is_a_subclass_of"], None)):
          if not isInstantiated(str(o)):
            # print("debugging -- remove", str(s), MYTerms[p], str(o))
            from_graph.remove((s, p, o))
            n_i = instantiated[c_original][n]
            o_original = getID(str(o))
            o_enum = self.container_graph.incrementNodeEnumerator(c_original, o_original)
            o_i = makeID(o_original, o_enum)
            instantiated[c_original][o_original] = o_i
            # print("debugging -- add", n_i, MYTerms[p], o_i)

            from_graph.add((Literal(n_i), p, Literal(o_i)))

    for s, p, o in from_graph.triples((None, RDFSTerms["is_a_subclass_of"], None)):
      if (not isInstantiated(str(s))) and (not isInstantiated(o)):
        o_original = getID(str(o))
        if o_original in instantiated[c_original]:
          # print("debugging -- remove", s, MYTerms[p], o)
          from_graph.remove((s, p, o))
          o_i = instantiated[c_original][o_original]
          # print("debugging -- add", s, p, o_i)
          from_graph.add((s, p, Literal(o_i)))

    # for s, p, o in from_graph:
    #   print(s, p, o)

    if c in instantiated[c_original]:
      c_store = instantiated[c_original][c]
      del self.RDFConjunctiveGraph[c]
      self.RDFConjunctiveGraph[c_store] = from_graph
      # print("debugging -- put the graph into to conjunctive graph")
      index = class_path.index(c)
      class_path[index] = c_store
    else:
      c_store = c

    ### end of the first class, the class where the instantiation took place, being modified

    c_previous = c_store #getID(c_store)
    for c in reversed(class_path[:-1]):
      c_original = getID(c)
      # print("debugging -- >>>>>>>>>>>> ", class_path, c)
      nodes = paths_in_classes[c].split(DELIMITERS["path"])
      from_graph = copy.deepcopy(self.RDFConjunctiveGraph[c])
      # updated_nodes = []
      instantiated[c_original] = {}  # OrderedDict()  # here it is set
      for node_no in reversed(range(1, len(nodes))):
        # print(nodes[node_no], nodes[node_no - 1])
        for s, p, o in from_graph.triples(
                (Literal(nodes[node_no]), RDFSTerms["is_a_subclass_of"], Literal(nodes[node_no - 1]))):
          ss = str(s)
          os = str(o)
          s_original = getID(ss)
          o_original = getID(os)
          # print(ss, MYTerms[p], os)
          if (ss not in instantiated[c_original]) \
                  and (os not in instantiated[c_original]):
            #(not isInstantiated(ss)) and (not isInstantiated((os))):
            enum = self.container_graph.incrementNodeEnumerator(c_original, s_original)
            s_i = makeID(s, enum)
            enum = self.container_graph.incrementNodeEnumerator(c_original, o_original)
            o_i = makeID(o, enum)
            from_graph.remove((s, p, o))
            from_graph.add((s_i, p, o_i))
            instantiated[c_original][s_original] = str(s_i)
            instantiated[c_original][o_original] = str(o_i)
          elif (not isInstantiated(ss) and isInstantiated(os)):
            enum = self.container_graph.incrementNodeEnumerator(c_original, s_original)
            s_i = makeID(s, enum)
            from_graph.remove((s, p, o))
            from_graph.add((Literal(s_i), p, o))
            instantiated[c_original][s_original] = str(s_i)

      for s, p, o in from_graph.triples((None, RDFSTerms["is_a_subclass_of"], None)):
        if (not isInstantiated(str(s))) \
                and (not isInstantiated(str(o))) \
                and (str(o) in instantiated[c_original]):
          o_original = getID(str(o))
          o_i = instantiated[c_original][o_original]
          from_graph.add((s, p, Literal(o_i)))
          from_graph.remove((s, p, o))

      # fix links
      # print("\n==== ")
      triple_new = None
      triple = None
      if c_previous:
        for s, p, o in from_graph.triples((None, RDFSTerms["link_to_class"], None)):
          s_original = getID(str(s))
          o_original = getID(str(o))
          # print("debugging --found ", str(s), MYTerms[p], str(o))
          if (str(s_original) in instantiated[getID(c_previous)]) and (str(o_original) in instantiated[c_original]):
            triple_new = [instantiated[getID(c_previous)][s_original], MYTerms[p], instantiated[c_original][o_original]]
            # print("debugging -- link to be established", str(s), str(o), "--", triple_new)
            triple_new = (Literal(triple_new[0]), p, Literal(triple_new[2]))
            triple = (s, p, o)
        if triple_new:
          from_graph.remove(triple)
          from_graph.add(triple_new)

      c_previous = c_original

      c_store = c
      if c in instantiated:
        node_no = self.container_graph.incrementClassEnumberator(c)
        c_i = makeID(c, node_no)
        index = class_path.index(c)
        class_path[index] = c_i
        c_store = c_i
        instantiated[c][c] = c_i
        # del instantiated[c]
        del self.RDFConjunctiveGraph[c]

      self.RDFConjunctiveGraph[c_store] = from_graph

    # finally, update paths in classes
    new_paths_in_classes = {}
    for c in list(paths_in_classes.keys()):
      c_original = getID(c)
      nodes = paths_in_classes[c].split(DELIMITERS["path"])
      new_nodes = []
      for n in nodes:
        if n in instantiated[c_original]:
          new_nodes.append(instantiated[c_original][n])
        else:
          # print(">>>>>>>>>>>troubles", c, c_original, n)
          new_nodes.append(n)

      if not isInstantiated(c):
        c_i = instantiated[c][c]
      else:
        c_i = c
      new_paths_in_classes[c_i] = DELIMITERS["path"].join(new_nodes)

    return class_path, new_paths_in_classes

  # def overlayContainerGraph(self, graph_ID, rdf_data_class_graph):
  #   # print("debugging -- overlay container graph")
  #   self.graph_ID = graph_ID
  #   self.RDFConjunctiveGraph[graph_ID] = rdf_data_class_graph
  #
  #   container_graph_ID = getID(graph_ID)
  #   container_class_graph = self.container_graph.RDFConjunctiveGraph[container_graph_ID]
  #
  #   working_graph = Graph()
  #
  #   if len(rdf_data_class_graph) == 0:
  #     for s, p, o in container_class_graph.triples((None, None, None)):
  #       if str(s) == container_graph_ID:
  #         s_ = Literal(graph_ID)
  #       else:
  #         s_ = s
  #       if str(o) == container_graph_ID:
  #         o_ = Literal(graph_ID)
  #       else:
  #         o_ = o
  #       working_graph.add((s_, p, o_))
  #
  #     for d_s, d_p, d_o in rdf_data_class_graph.triples((None, None, None)):
  #       # print(">>> %s, %s, %s" % (d_s, d_p, d_o))
  #       for s, p, o in container_class_graph.triples((None, None, None)):
  #         _s = getID(str(s))
  #         _o = getID(str(o))
  #         t_s = Literal(_s)
  #         t_o = Literal(_o)
  #         l_s = (t_s == d_s)
  #         l_p = (p == d_p)
  #         l_o = (t_o == d_o)
  #         if l_s and l_p and l_o:
  #           working_graph.add((s, p, o))
  #         elif l_s and l_p:
  #           working_graph.add((t_s, p, d_o))
  #         elif l_o and l_p:
  #           working_graph.add((d_s, p, t_o))
  #         else:
  #           working_graph.add((s, p, o))
  #   return working_graph

  def makeDotGraph(self):
    graph_overall = Graph()
    for cl in self.RDFConjunctiveGraph:
      for t in self.RDFConjunctiveGraph[cl].triples((None, None, None)):
        s, p, o = t
        # print("debugging -- graph adding", str(s), MYTerms[p], str(o))
        graph_overall.add(t)
    dot = plot(graph_overall, self.txt_class_names)
    # print("debugging -- dot")
    graph_name = self.txt_root_class
    dot.render(graph_name, directory=ONTOLOGY_DIRECTORY, view=True)
    return dot


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
    # global class_path
    # global data_container_number
    # global data_container
    # global working_tree

    self.FrontEnd = FrontEnd
    self.changed = False

    self.ContainerGraph = ContainerGraph()
    # data_container = {}
    self.working_tree = None

    self.ui_state("start")
    self.current_node = None
    self.current_class = None
    self.current_subclass = None
    self.data_container_number = 0
    self.class_path = []

    self.path_at_transition = {}  # Note: path at the point of transition to another class. Key: class_ID

    self.instanceEnumerator = Enumerator()

    self.automaton = self.automaton()

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
    global is_container_class

    subject, predicate, obj = current_event_data["triple"]
    graph_ID = current_event_data["class"]
    path = current_event_data["path"]

    self.current_node = subject

    is_data_class = self.working_tree.isClass(subject) or (not subject)
    is_container_class = self.ContainerGraph.isClass(subject)
    is_sub_class = self.working_tree.isSubClass(subject, graph_ID)
    is_primitive = self.working_tree.isPrimitive(subject)
    is_value = self.working_tree.isValue(predicate)
    is_integer = self.working_tree.isInteger(predicate)
    is_comment = self.working_tree.isComment(predicate)
    is_string = self.working_tree.isString(predicate)
    is_linked = (predicate == "link_to_class")
    is_instantiated_object = isInstantiated(obj)

    debugging = True
    if debugging:
      txt = "selection has data: %s    " % current_event_data
      if is_data_class: txt += " & class"
      if is_container_class: txt += " & container_class"
      if is_sub_class: txt += " & subclass"
      if is_primitive: txt += " & primitive"
      if is_value: txt += " & value"
      if is_linked: txt += " & is_linked"
      if is_instantiated_object: txt += " & instantiated"
      if is_integer: txt += " & integer"
      if is_comment: txt += " & comment"
      if is_string: txt += " & string"
      print("selection : %s\n" % txt)

    if is_primitive:
      if (not isInstantiated(subject)):
        if is_integer:
          self.ui_state("instantiate_integer")
        elif is_string:
          self.ui_state("instantiate_string")
        else:
          self.ui_state("show_tree")
        return

    if is_sub_class and (not is_linked) and is_instantiated_object:
      dialog = self.FrontEnd.dialogYesNo(message="add new ")
      if dialog == "YES":
        self.__addBranch()
      elif dialog == "NO":
        pass



    if is_linked:
      # print("shifting event data :", current_event_data)
      # self.previous_class = self.current_class
      self.current_class = subject
      self.__makeWorkingTree()
      self.__shiftClass()

  def __addBranch(self):
    graph = self.working_tree.container_graph.extractSubgraph(getID(self.current_node),
                                                              getID(self.current_class))
    print("debugging -- subgraph", graph)

    # now one needs to connect this branch to the working graph at the location below the current node
    # 1st find the below node



  def __gotInteger(self):
    global current_event_data
    global automaton_next_state
    # global class_path

    # subject, predicate, obj = current_event_data["triple"]
    value = current_event_data["integer"]
    path = current_event_data["path"]

    paths_in_classes = self.path_at_transition
    paths_in_classes[self.current_class] = path
    self.class_path, paths_in_classes = self.working_tree.instantiateAlongPath(paths_in_classes,
                                                                               self.class_path,
                                                                               )
    # need to update path at transitions too
    self.path_at_transition = {}
    for c in self.class_path[:-1]:
      self.path_at_transition[c] = paths_in_classes[c]

    # make global path
    global_path_nodes = []
    global_node_IDs = []
    nodes = self.__extractNodesFromPaths(paths_in_classes)
    for n in nodes:
      global_path_nodes.append(getID(n))
      global_node_IDs.append(getIDNo(n))

    global_path = DELIMITERS["path"].join(global_path_nodes)
    global_IDs = DELIMITERS["instantiated"].join(global_node_IDs)

    # print("debugging -- global path", global_path)

    self.working_tree.data.addInteger(global_path, global_IDs, value)

    # self.working_tree.printMe("after instantiate")
    current_event_data = {"class": self.class_path[-1]}
    self.__shiftToSelectedClass()

  def __extractNodesFromPaths(self, paths_in_classes):
    """
    extracts a dictionary of nodes one entry for each active class
    """
    nodes = {}
    for c in self.class_path:
      nodes[c] = paths_in_classes[c].rstrip(DELIMITERS["path"]).split(DELIMITERS["path"])  # drop last delimiter
    return nodes

  def __clearInteger(self):
    self.FrontEnd.controls("selectors", "integer", "populate", {"value": 0})

  def __clearString(self):
    self.FrontEnd.controls("selectors", "string", "clear", )

  def __makeDotPlot(self):
    # global working_tree
    self.working_tree.makeDotGraph()

  def __updateTree(self):
    global current_event_data
    global automaton_next_state
    # print(">>>", current_event_data, automaton_next_state)

  def __shiftToSelectedClass(self):
    global current_event_data

    # print("shifting event data :", current_event_data)

    self.current_class = current_event_data["class"]

    self.__makeWorkingTree()
    self.__shiftClass()

  def __shiftClass(self):
    # global class_path
    global current_event_data

    if "path" in current_event_data:
      transition_path = "/".join(current_event_data["path"].split(DELIMITERS["path"])[:-1]) + DELIMITERS["path"]
      previous_class = self.class_path[-1:][0]
      self.path_at_transition[previous_class] = transition_path
      # print("debugging -- transition -- ", previous_class, self.current_class, self.path_at_transition)
    # else:
    #   print("debugging -- no current path defined")

    class_ID = self.current_class
    if class_ID not in self.class_path:
      self.class_path.append(class_ID)
    else:
      i = self.class_path.index(class_ID)
      self.class_path = self.class_path[:i + 1]
    pass

    self.FrontEnd.controls("selectors", "classTree", "populate", self.quads, self.current_class)
    self.FrontEnd.controls("selectors", "classList", "populate", self.class_path)

    # print(">>>", current_event_data, automaton_next_state)

  def __makeFirstDataRoot(self, container_root_class, data_ID):
    # global data_container_number

    root_class = container_root_class + DELIMITERS["instantiated"] + str(data_ID)
    return root_class

  def __makeWorkingTree(self):
    # global data_container_number
    global data_container
    # global working_tree
    global is_container_class
    # print("debugging make tree")

    if (self.data_container_number == 0) or is_container_class:
      self.working_tree.makeAllListsForAllGraphs()
    self.quads = convertRDFintoInternalMultiGraph(self.working_tree.RDFConjunctiveGraph[self.current_class],
                                                  self.current_class)
    print("debugging -- the quads", self.quads)

  def __gotNumber(self):
    global current_event_data
    path = current_event_data["path"]
    number = current_event_data["integer"]
    # print("debugging -- got path and number:", path, number)

  def processEvent(self, state, Event, event_data):
    # Note: cannot be called from within backend -- generates new name space
    global gui_state
    global current_event_data
    global automaton_next_state
    global action
    # global data_container_number
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

  def automaton(self):
    automaton = {
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
                                                                   self.__clearInteger,
                                                                   self.__clearString,
                                                                   ],
                                                    "gui_state" : "NoSet"},
                                       },
            "wait_for_ID"           : {"got_integer": {"next_state": "show_tree",
                                                       "actions"   : [self.__gotNumber,
                                                                      self.__gotInteger],
                                                       "gui_state" : "show_tree"},
                                       # "has_no_ID" : {"next_state": "wait_for_ID",
                                       #                "actions"   : [None],
                                       #                "gui_state" : "has_no_ID"},
                                       # "has_ID"    : {"next_state": "wait_for_ID",
                                       #                "actions"   : [None],
                                       #                "gui_state" : "has_ID"},
                                       # "got_no_ID" : {"next_state": "show_tree",
                                       #                "actions"   : [None],
                                       #                "gui_state" : "show_tree"},
                                       # "add_new_ID": {"next_state": "show_tree",
                                       #                "actions"   : [self.__updateDataWithNewID],
                                       #                "gui_state" : "show_tree"},
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

    return automaton

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
    # elif state == "input_identifier":
    #   show = {"buttons": ["exit",
    #                       ],
    #           "groups" : [
    #                   "PrimitiveString"], }
    elif state == "show_tree":
      show = {"buttons"  : ["save",
                            "exit",
                            "visualise",
                            ],
              "selectors": ["classList",
                            "classTree"],
              }
    # elif state == "has_ID":  # ???
    #   show = {"buttons"  : ["save",
    #                         "exit",
    #                         "visualise",
    #                         "instantiate",
    #                         ],
    #           "selectors": ["classList",
    #                         "classTree"],
    #           }
    # elif state == "has_no_ID":  # ???
    #   show = {"buttons"  : ["save",
    #                         "exit",
    #                         "visualise",
    #                         "instantiate",
    #                         ],
    #           "selectors": ["classList",
    #                         "classTree"],
    #           }
    elif state == "instantiate_integer":
      show = {"buttons"  : ["instantiate",
                            "acceptInteger",
                            ],
              "selectors": ["classList",
                            "classTree",
                            "integer"],
              "groups"   : "integer"}
    elif state == "instantiate_string":
      show = {"buttons"  : ["instantiate",
                            "acceptString",
                            ],
              "selectors": ["classList",
                            "classTree",
                            "string"],
              "groups"   : ["string"]}
    # elif state == "instantiate_item":
    #   show = {"buttons"  : ["instantiate",
    #                         ],
    #           "selectors": ["classList",
    #                         "classTree",
    #                         "integer"],
    #           "groups"   : "integer"}
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
    # elif state == "selected_value":
    #   show = {"buttons": ["save",
    #                       "exit", ],
    #           "groups" : [
    #                   "ValueElucidation",
    #                   ]
    #           }
    else:
      show = []
      print("ooops -- no such gui state", state)

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


if __name__ == "__main__":
  quads = [('c_number', 'c', 'value', 'a'), ('integer', 'c_number', 'integer', 'a'), ('c', 'a', 'is_a_subclass_of', 'a'), ('b', 'a', 'is_a_subclass_of', 'a'), ('d', 'b', 'is_a_subclass_of', 'a'), ('A', 'd', 'link_to_class', 'a')]
  extracts = []
  extractSubTree(quads,'b', extracts)
  print(extracts)