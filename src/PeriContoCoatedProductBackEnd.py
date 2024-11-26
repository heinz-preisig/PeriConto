"""
Backend to the construction of a data base for coatings formulations

The data are stored in triple stored in triple stores

rule: notation
an instantiated "node" is <<name>>:<<ID>>

"""

import copy
import os.path

DELIMITERS = {"instantiated": ":",
              "path"        : "/"}

from rdflib import Graph
from rdflib import Literal

# from graphviz import Digraph
import graphviz

from PeriConto import MYTerms
from PeriConto import ONTOLOGY_DIRECTORY
from PeriConto import PRIMITIVES
from PeriConto import RDFSTerms
from PeriConto import VALUE
from PeriConto import getData
from PeriConto import makeRDFCompatible
from PeriConto import DIRECTION

EDGE_COLOUR = {
        "is_a_subclass_of": "blue",
        "link_to_class"   : "red",
        "value"           : "black",
        "comment"         : "green",
        "integer"         : "darkorange",
        "string"          : "cyan",
        }


def copyRDFGraph(G_original):
  G_copy = Graph()
  for triple in G_original:
    G_copy.add(triple)
  return G_copy


def plot(graph, class_names=[""]):
  """
  Create Digraph plot
  color names : https://graphviz.org/doc/info/colors.html
  """
  dot = graphviz.Digraph()
  # Add nodes 1 and 2
  suffix = 0
  for s, p, o in graph.triples((None, None, None)):
    ss = str(s)
    ss_ = str(ss).replace(":", "-")
    sp = str(p)
    so = str(o)
    so_ = str(o).replace(":", "-")
    s_ID = getID(str(s))
    if s_ID in PRIMITIVES:  # primitives are not having a unique name so we equip them with an incremental suffix
      if isInstantiated(ss):
        ss_ += "_%s" % suffix
        suffix += 1
    o_ID = getID(str(o))
    if o_ID in PRIMITIVES:
      if isInstantiated(so):
        so_ += "_%s" % suffix
        suffix += 1
    if getID(ss) in class_names:
      dot.node(ss_, color='red', style = "filled", fillcolor="lightcoral", shape="none")
    elif getID(so) in PRIMITIVES:
      if isInstantiated(so):
        dot.node(so_, color='green',  style='filled', fillcolor="yellow", shape="none")
      else:
        dot.node(so_, color='green',  style='filled', fillcolor="gray", shape="none")
    else:
      dot.node(ss_)


    if so == class_names[0]:
      dot.node(so_, style="filled", fillcolor="red", shape="none")
    else:
      dot.node(so_)

    # if so in class_names:
    #   dot.node(so_, color='red', style = "filled", fillcolor="",  shape="rectangle")
    # else:
    #   dot.node(so_)

    my_p = MYTerms[p]
    if DIRECTION[my_p] == 1:
      dot.edge(ss_, so_,
               # label=my_p,
               color=EDGE_COLOUR[my_p])
    else:
      dot.edge(ss_, so_,
               # label=my_p,
               color=EDGE_COLOUR[my_p])

  return dot

def LegendPlot():

  """
  Create Digraph plot
  """
  dot = graphviz.Digraph()

  atr = {"label"   : "Legend",
         "style"   : "solid",
         "rankdir" : "TB",
         "bb"      : "rectangle",
         # "ranksep" : "0.05",
         # "nodesep" : "0.01",
         "labelloc": "b",
         # "len"     : "0",
         "shape"   : "none",
         }

  l = graphviz.Digraph(node_attr=atr, name="Legend")  # {"style": "filled", "shape": 'none', "rankdir":"LR"})

  # l.node("legend", label="Legend", shape="box")
  for i in EDGE_COLOUR:
    s = i + " "
    l.node(s, label=i)
    l.node("o", label="o")
    l.edge(s, "o", color=EDGE_COLOUR[i])

  # l.edge("legend","o")
  dot.subgraph(l)

  # Visualize the graph
  # dot.node('tab', shape="none", label='''<<TABLE>
  #  <TR>
  #    <TD>"boarder="0" left</TD>
  #    <TD>right</TD>
  #  </TR>
  # </TABLE>>''')
  #

  # l = graphviz.Digraph( node_attr=atr)
  #
  # l.node("class", label="Class")
  # l.node("abstract", label = "Abstract")
  # l.node("interface", label = "Interface")
  # dot.subgraph(l)

  return dot


def debuggPlotAndRender(graph, file_name, debugg):
  """
  @graph is an RDF graph
  @file_name is to generate a file name
  @debugg  is a convenience variable to help debugging
  """
  if debugg:
    dot = plot(graph)
    dot.render(file_name, view=True)

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
  for f, s, p, graphID in quads:
    if p not in ["value"] + PRIMITIVES:
      graph.add((Literal(f), RDFSTerms[p], Literal(s)))
    else:
      graph.add((Literal(s), RDFSTerms[p], Literal(f)))
  return graph


def extractSubTree(quads, root, extracts=[], stack=[]):
  for s, o, p, graphID in quads:
    if o == root:
      extracts.append((s,o,p,graphID))
      if o not in stack:
        extractSubTree(quads, s, extracts, stack)

  if o == root:
    stack.append(o)


def debuggPrintGraph(graph, debug, text=""):
  if debug:
    print("\ndebugging: %s"%text)
    for s, p, o in graph.triples((None, None, None)):
      print(str(s), MYTerms[p], str(o))


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
    self.RDFConjunctiveGraph = {self.txt_root_class: Graph(identifier=root_class)}
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

      for s, p, o in graphs_internal[g]:
        self.addGraphGivenInInternalNotation(s, p, o, g)

    return self.txt_root_class

  def addGraphGivenInInternalNotation(self, subject_internal, predicate_internal, object_internal, graph_ID):
    rdf_subject = makeRDFCompatible(subject_internal)
    rdf_object = makeRDFCompatible(object_internal)
    rdf_predicate = RDFSTerms[predicate_internal]
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    self.RDFConjunctiveGraph[graph_ID].add((rdf_subject, rdf_predicate, rdf_object))

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


# def makeListBasedOnPredicates(rdf_graph, rdf_predicate):
#   subclasslist = []
#   for s, p, o in rdf_graph.triples((None, RDFSTerms[rdf_predicate], None)):
#     subclasslist.append(str(s))  # (str(s), txt_class, str(o)))
#   return subclasslist


# def makeLinkListBasedOnPredicates(rdf_graph, txt_class, rdf_predicate):
#   subclasslist = []
#   for s, p, o in rdf_graph.triples((None, RDFSTerms[rdf_predicate], None)):
#     subclasslist.append((str(s), txt_class, str(o)))
#   return subclasslist


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
    v = self.enumerators["nodes_in_classes"][class_ID][node_ID]
    v += 1
    self.enumerators["nodes_in_classes"][class_ID][node_ID] = v
    return v

  def incrementPrimitiveEnumerator(self, primitive):
    v = self.enumerators[primitive]
    v += 1
    self.enumerators[primitive] = v
    return v


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
    print("debugging -- integer add key", key, value)
    if key not in self.integers:
      self.integers[key] = value
    else:
      print("adding integer >>> error")

  def addString(self, path, IDs, string):  # addString(global_path, global_IDs, value)
    path_enum = self.addPath(path)
    key = (path_enum, IDs)
    print("debugging -- string add key", key, string)
    if key not in self.integers:
      self.integers[key] = string
    else:
      print("adding string >>> error")

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

    # self.printMe("copied into the working tree")

  def instantiateAlongPath(self, paths_in_classes, class_path):

    debug = False


    print("debugging -- class path and paths in classes", class_path, paths_in_classes)

    instantiated = {}

    # we start at the end, where the primitive was just instantiated
    c = class_path[-1]
    c_original = getID(c)
    from_graph = copy.deepcopy(self.RDFConjunctiveGraph[c])

    debuggPrintGraph(from_graph, debug, text="starting")
    # print("debugging -- >>>>>>>>>>>> ", class_path, c)
    nodes = paths_in_classes[c].split(DELIMITERS["path"])

    instantiated[c_original] = {}  # keep track on what node in the path has been instantiated

    primitive = nodes[-1]  # get the primitive
    primitive_name = nodes[-2]  # that's the node with the name for the primitive
    value_name = nodes[-3]  # that's the quantity given a value with the name being the node [-2]

    if primitive not in PRIMITIVES:
      print("error >>>>>>>  %s must be a primitive" % primitive)
      return

    # both must not be instantiated
    if isInstantiated(primitive) or isInstantiated(primitive_name) or isInstantiated(value_name):
      print("error >>>>>>>>  neither node can be instantiated", primitive, primitive_name, value_name)
      return

    primitive_enum = self.container_graph.incrementPrimitiveEnumerator(getID(primitive))
    primitive_i = makeID(primitive, primitive_enum)
    instantiated[c_original][primitive] = primitive_i

    primitive_name_enum = self.container_graph.incrementNodeEnumerator(c_original, getID(primitive_name))
    primitive_name_i = makeID(primitive_name, primitive_name_enum)
    instantiated[c_original][primitive_name] = primitive_name_i

    value_name_enum =self.container_graph.incrementNodeEnumerator(c_original,  getID(value_name))
    value_name_i = makeID(value_name, value_name_enum)
    instantiated[c_original][value_name] = value_name_i

    from_graph.remove((Literal(primitive_name), RDFSTerms[primitive], Literal(primitive)))
    from_graph.add((Literal(primitive_name_i), RDFSTerms[primitive], Literal(primitive_i)))


    from_graph.remove((Literal(value_name), RDFSTerms["value"], Literal(primitive_name)))
    from_graph.add((Literal(value_name_i), RDFSTerms["value"], Literal(primitive_name_i)))

    node_list = reversed(nodes[1:-2])
    stop = False
    for n in node_list:
      for s, p, o in from_graph.triples((Literal(getID(n)), RDFSTerms["is_a_subclass_of"], None)):
        n_i = instantiated[c_original][n]
        if isInstantiated((str(o))):  # hit an instantiated node
          from_graph.remove((s, p, o))
          from_graph.add((Literal(n_i), p, o))
          # print("debugging - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> stop 1")
          stop = True
          debuggPrintGraph(from_graph, debug, text="stop 1")
          break
        else:
          o_original = getID(str(o))
          o_enum = self.container_graph.incrementNodeEnumerator(c_original, o_original)
          o_i = makeID(o_original, o_enum)
          instantiated[c_original][o_original] = o_i
          from_graph.remove((s, p, o))
          from_graph.add((Literal(n_i), p, Literal(o_i)))

    # debuggPrintGraph(from_graph, debug, text="completed node list")

    for n in instantiated[c_original]:
      n_i = instantiated[c_original][n]
      for s, p, o in from_graph.triples((None, RDFSTerms["is_a_subclass_of"], Literal(n))):
        from_graph.remove((s, p, o))
        from_graph.add((s, p, Literal(n_i)))

    # debuggPrintGraph(from_graph, debug)

    if c in instantiated[c_original]:
      c_store = instantiated[c_original][c]
      # del self.RDFConjunctiveGraph[c]  # todo: here it is deleted
      self.RDFConjunctiveGraph[c_store] = from_graph
      # print("debugging -- put the graph into to conjunctive graph")
      index = class_path.index(c)
      class_path[index] = c_store
    else:
      c_store = c

    if not isInstantiated(c):
      c_i = instantiated[c][c]
    else:
      c_i = c

    t = self.updatePathsInClasses(c, instantiated, paths_in_classes)
    del paths_in_classes[c]
    paths_in_classes[c_i] = t

    if stop:
      self.RDFConjunctiveGraph[c_store] = from_graph
      return class_path, paths_in_classes

    ### end of the first class, the class where the instantiation took place, being modified

    for c in reversed(class_path[:-1]):
      linked_node = nodes[0]  # this is the link to the previous class

      # linked_node_i = instantiated[c_original][linked_node]
      c_previous_original = c_original

      c_original = getID(c)
      # print("debugging -- >>>>>>>>>>>> ", class_path, c)
      nodes = paths_in_classes[c].split(DELIMITERS["path"])
      linked_to_node = nodes[-2]
      from_graph = copy.deepcopy(self.RDFConjunctiveGraph[c])

      debuggPrintGraph(from_graph, debug, text= "before handling the links")

      instantiated[c_original] = {}  # OrderedDict()  # here it is set
      for s, p, o in from_graph.triples((Literal(linked_node), RDFSTerms["link_to_class"], Literal(linked_to_node))):
        from_graph.remove((s, p, o))
        o_enum = self.container_graph.incrementNodeEnumerator(c_original, str(o))
        o_i = makeID(str(o), o_enum)
        instantiated[c_original][str(o)] = o_i
        s_i = instantiated[c_previous_original][str(s)]
        from_graph.add((Literal(s_i), p, Literal(o_i)))

      debuggPrintGraph(from_graph, debug, text="after handling the links")

      node_list = reversed(nodes[0:-1])
      for n in node_list:

        for s, p, o in from_graph.triples((Literal(getID(n)), RDFSTerms["is_a_subclass_of"], None)):
          if n in instantiated[c_original]:
            n_i = instantiated[c_original][n]
          else:
            n_enum = self.container_graph.incrementNodeEnumerator(c_original, getID(n))
            n_i = makeID(n, n_enum)
          if isInstantiated((str(o))):  # hit an instantiated node
            from_graph.remove((s, p, o))
            from_graph.add((Literal(n_i), p, o))
            # print("debugging - >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> stop 2")
            stop = True
            break
          else:
            o_original = getID(str(o))
            o_enum = self.container_graph.incrementNodeEnumerator(c_original, o_original)
            o_i = makeID(o_original, o_enum)
            instantiated[c_original][o_original] = o_i
            from_graph.remove((s, p, o))
            from_graph.add((Literal(n_i), p, Literal(o_i)))

      # debuggPrintGraph(from_graph, debug)

      for n in instantiated[c_original]:
        n_i = instantiated[c_original][n]
        for s, p, o in from_graph.triples((None, RDFSTerms["is_a_subclass_of"], Literal(n))):
          from_graph.remove((s, p, o))
          from_graph.add((s, p, Literal(n_i)))

      debuggPrintGraph(from_graph, debug, text="putting things back")

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

      if not isInstantiated(c):
        c_i = instantiated[c][c]
      else:
        c_i = c
      t = self.updatePathsInClasses(c, instantiated, paths_in_classes)
      del paths_in_classes[c]
      paths_in_classes[c_i] = t
      if stop:
        return class_path, paths_in_classes

    return class_path, paths_in_classes

  def updatePathsInClasses(self, c, instantiated, paths_in_classes):
    c_original = getID(c)
    nodes = paths_in_classes[c].split(DELIMITERS["path"])
    new_nodes = []
    for n in nodes:
      if n in instantiated[c_original]:
        new_nodes.append(instantiated[c_original][n])
      else:
        # print(">>>>>>>>>>>troubles", c, c_original, n)
        new_nodes.append(n)
    t = DELIMITERS["path"].join(new_nodes)
    return t

  def makeDotGraph(self):
    graph_overall = self.collectGraphs()
    class_names = list(self.RDFConjunctiveGraph.keys())
    dot = plot(graph_overall, class_names)
    graph_name = self.txt_root_class
    dot.render(graph_name, directory=ONTOLOGY_DIRECTORY, view=True)
    if not os.path.exists(os.path.join(ONTOLOGY_DIRECTORY, "legend.pdf")):
      # TODO: add button for legend
      leg = LegendPlot()
      leg.render("legend", directory=ONTOLOGY_DIRECTORY, view=True)
    return dot

  def collectGraphs(self):
    graph_overall = Graph()
    for cl in self.RDFConjunctiveGraph:
      for t in self.RDFConjunctiveGraph[cl].triples((None, None, None)):
        s, p, o = t
        graph_overall.add(t)
    # class_names = list(self.RDFConjunctiveGraph.keys())
    # dot = plot(graph_overall, class_names)
    # graph_name = self.txt_root_class
    return graph_overall

  def extractSubgraph(self, root, graph_ID):
    """
    extract an RDF-subgraph from an RDF-Graph given a root as a string, a label
    it is done via the quads generation that ignore the directionality
    """
    quads = convertRDFintoInternalMultiGraph(self.container_graph.RDFConjunctiveGraph[graph_ID], graph_ID)
    extracts = []  #TODO: add button for legend
    extractSubTree(quads, root, extracts)  # as quads
    graph = convertQuadsGraphIntoRDFGraph(extracts)
    linked_classes = []
    debuggPlotAndRender(graph,"adding", True)
    c_next = None
    for s,p,o in graph.triples((None, RDFSTerms["link_to_class"],None)):
      c_next = getID(str(s))
      if c_next:
        linked_classes.append(c_next)
        self.getLinkedGraphs(c_next, linked_classes, stack=[])

    return graph, linked_classes

  def getLinkedGraphs(self, c_current, linked_classes, stack=[]):
    graph = self.container_graph.RDFConjunctiveGraph[c_current]
    stack.append(c_current)
    for s,p,o in graph.triples((None, RDFSTerms["link_to_class"],None)):
      c_next = getID(str(s))
      if c_next not in stack:
        linked_classes.append(c_next)
        stack.append(c_next)
        self.getLinkedGraphs(c_next, linked_classes, stack= stack)

def isInstantiated(ID):
  id = str(ID)
  # print("debugging ==", id,(DELIMITERS["instantiated"] in id))
  return DELIMITERS["instantiated"] in id


def getID(ID):
  if DELIMITERS["instantiated"] in ID:
    container_graph_ID, instance_ID = ID.split(DELIMITERS["instantiated"])
  else:
    container_graph_ID = ID
  return container_graph_ID


def getIDNo(ID):
  if DELIMITERS["instantiated"] in ID:
    container_graph_ID, instance_ID = ID.split(DELIMITERS["instantiated"])
  else:
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


class Stack(dict):
  def __init__(self):
    dict.__init__(self)

  def push(self, key, item):
    self[key] = item

  def pop(self, key):
    v = self[key]
    return v

  def reduce(self, keys):
    delete_key = []
    for k in self:
      if k not in keys:
        delete_key.append(k)
    for k in delete_key:
      del self[k]


class BackEnd:

  def __init__(self, FrontEnd):

    global state

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

    self.path_at_transition = Stack()  # Note: path at the point of transition to another class. Key: class_ID

    self.instanceEnumerator = Enumerator()

    self.automaton = self.automaton()

  def __askForFileName(self):
    global current_event_data
    global automaton_next_state

    state = automaton_next_state

    self.FrontEnd.fileNameDialog(state, "file_name",
                                 "ontology",
                                 ONTOLOGY_DIRECTORY,
                                 "*",
                                 "exit")

  def __loadOntology(self):
    global current_event_data

    file_name = current_event_data["file_name"]

    event_data = current_event_data
    self.root_class_container = self.ContainerGraph.load(file_name)

    self.ContainerGraph.printMe("loaded")

    self.working_tree = WorkingTree(self.ContainerGraph)
    self.txt_class_names = list(self.working_tree.container_graph.RDFConjunctiveGraph.keys())

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
      self.current_class = subject
      self.__makeWorkingTree()
      self.__shiftClass()

  def __addBranch(self):
    debug_plot = True
    debug_print = False
    root = getID(self.current_node)
    c_original = getID(self.current_class)
    sub_graph, linked_classes = self.working_tree.extractSubgraph(root, c_original)

    debuggPrintGraph(sub_graph, debug_print)
    debuggPlotAndRender(sub_graph, "wg_to_be_added", debug_plot)

    debuggPlotAndRender(sub_graph, "subgraph", debug_plot)

    # print("debugging -- linked_classes", linked_classes)

    w_graph= self.working_tree.RDFConjunctiveGraph[self.current_class] + sub_graph

    debuggPlotAndRender(w_graph, "wg_extended", debug_plot)

    debuggPrintGraph(self.working_tree.RDFConjunctiveGraph[self.current_class], debug_print)
    debuggPrintGraph(w_graph, debug_print)

    for s, p, o in w_graph.triples(
            (Literal(self.current_node), RDFSTerms["is_a_subclass_of"], None)):
      print("debugging -- obj:", str(o))
      to_connect = getID(self.current_node)
      w_graph.add((Literal(root), p, Literal(str(o))))

    self.working_tree.RDFConjunctiveGraph[self.current_class] = w_graph

    debuggPlotAndRender(w_graph, "wg_extended_linked", debug_plot)

    for c in linked_classes:
      self.working_tree.RDFConjunctiveGraph[c] = copy.copy(self.working_tree.container_graph.RDFConjunctiveGraph[c])

    self.__makeWorkingTree()


  def __gotInteger(self):
    global current_event_data
    global automaton_next_state

    value = current_event_data["integer"]
    path = current_event_data["path"]

    global_IDs, global_path = self.__preparteInstantiation(path)
    self.working_tree.data.addInteger(global_path, global_IDs, value)

    self.ui_state("show_tree")
    current_event_data = {"class": self.class_path[-1]}

  def __preparteInstantiation(self, path):
    paths_in_classes = copy.copy(self.path_at_transition)  # Note: this was a hard one
    paths_in_classes[self.current_class] = path
    self.class_path, paths_in_classes = self.working_tree.instantiateAlongPath(paths_in_classes,
                                                                               self.class_path,
                                                                               )
    for key in paths_in_classes:
      item = paths_in_classes[key]
      self.path_at_transition.push(key, item)
    self.path_at_transition.reduce(self.class_path[:-1])
    # make global path
    if not paths_in_classes:
      print("debugging -- troubles paths_in_classes is empty")
    global_path, global_IDs = self.__extractGlobalNodesAndIDsFromPaths(paths_in_classes)
    return global_IDs, global_path

  def __gotString(self):
    global current_event_data
    global automaton_next_state

    value = current_event_data["string"]
    path = current_event_data["path"]

    global_IDs, global_path = self.__preparteInstantiation(path)

    self.working_tree.data.addString(global_path, global_IDs, value)

    self.ui_state("show_tree")

    current_event_data = {"class": self.class_path[-1]}
    # self.__shiftToSelectedClass()

  def __extractGlobalNodesAndIDsFromPaths(self, paths_in_classes):
    """
    extracts the global path and the associated IDs
    """
    nodes = []
    for c in self.class_path:
      nodes.extend(paths_in_classes[c].rstrip(DELIMITERS["path"]).split(DELIMITERS["path"]))  # drop last delimiter

    global_path_nodes = []
    global_node_IDs = []
    for n in nodes:
      global_path_nodes.append(getID(n))
      global_node_IDs.append(getIDNo(n))
    global_path = DELIMITERS["path"].join(global_path_nodes)
    try:
      global_IDs = DELIMITERS["instantiated"].join(global_node_IDs)
    except:
      print("debugging -- problems with global_path_nodes")
    return global_path, global_IDs

  def __clearInteger(self):
    self.FrontEnd.controls("selectors", "integer", "populate", {"value": 0})

  def __clearString(self):
    self.FrontEnd.controls("selectors", "string", "clear", )

  def __makeDotPlot(self):
    # global working_tree
    return
    self.working_tree.makeRDFDotGraph()

  #
  def __makeFirstDataRoot(self, container_root_class, data_ID):

    root_class = container_root_class + DELIMITERS["instantiated"] + str(data_ID)
    return root_class

  def __makeWorkingTree(self):
    global data_container
    global is_container_class

    self.quads = convertRDFintoInternalMultiGraph(self.working_tree.RDFConjunctiveGraph[self.current_class],
                                                  self.current_class)

    gugus = convertQuadsGraphIntoRDFGraph(self.quads)
    debuggPlotAndRender(gugus, "made_quads", True)
    gugus = self.working_tree.collectGraphs()
    debuggPlotAndRender(gugus, "complete graph", True)

    # print("debugging -- the quads", self.quads)

  def processEvent(self, state, Event, event_data):
    # Note: cannot be called from within backend -- generates new name space
    global gui_state
    global current_event_data
    global automaton_next_state
    global action
    # global data_container

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
                                                       "actions"   : [self.__gotInteger],
                                                       "gui_state" : "show_tree"},
                                       "got_string" : {"next_state": "show_tree",
                                                       "actions"   : [self.__gotString],
                                                       "gui_state" : "show_tree"},
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
    elif state == "show_tree":
      show = {"buttons"  : ["save",
                            "exit",
                            "visualise",
                            ],
              "selectors": ["classList",
                            "classTree"],
              }
    elif state == "instantiate_integer":
      show = {"buttons"  : ["acceptInteger",
                            ],
              "selectors": ["classList",
                            "classTree",
                            "integer"],
              "groups"   : "integer"}
    elif state == "instantiate_string":
      show = {"buttons"  : ["acceptString",
                            ],
              "selectors": ["classList",
                            "classTree",
                            "string"],
              "groups"   : ["string"]}
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
  quads = [('c_number', 'c', 'value', 'a'), ('integer', 'c_number', 'integer', 'a'),
           ('c', 'a', 'is_a_subclass_of', 'a'), ('b', 'a', 'is_a_subclass_of', 'a'),
           ('d', 'b', 'is_a_subclass_of', 'a'), ('A', 'd', 'link_to_class', 'a')]
  extracts = []
  extractSubTree(quads, 'b', extracts)
  print(extracts)
