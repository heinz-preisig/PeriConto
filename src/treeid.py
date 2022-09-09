#!/usr/local/bin/python3
# encoding: utf-8

"""
===============================================================================
 rsource for manipulating trees
===============================================================================

Tree provides a multi-way tree of numerical identifiers, The identifier is an
integer. The identifier can then be used as a hash key in a dictionary to
establish an aliasing table to the actual object associated with the tree
nodes and leaves.

The structure of the tree is:

  node_id = {'parent': [father, grandfather, .... , root]
                 'children': [child 1, child2, ... ]
                 }

  thus each node knows its ancestors all the way up to the root.
  This facilitates easy handling of the tree data.



"""

__project__ = "ProcessModeller  Suite"
__author__ = "PREISIG, Heinz A"
__copyright__ = "Copyright 2015, PREISIG, Heinz A"
__since__ = "2016. 02. 09"
__license__ = "GPL planned -- until further notice for Bio4Fuel & MarketPlace internal use only"
__version__ = "6.00"
__email__ = "heinz.preisig@chemeng.ntnu.no"
__status__ = "beta"

import copy


def invertDict(dictionary):
  return dict(zip(dictionary.values(), list(dictionary.keys())))


# # TODO: replace the other walk methods with these functions
#
# def walkDepthFirstFnc(tree, id):
#   #   for child in self[id]['children']:
#   #     if self[child]['children'] == []:
#   #       #                print child, 'is a leave'
#   #       yield child, 'leave'
#   #     else:
#   #       yield child, 'node'
#   #       for x in self.walkDepthFirst(child):
#   #         self.walkDepthFirst(x)
#   #         #                    print 'walk' , x, '    kids ', self[x]['children']
#   #         yield x
#   #
#   # def get_depth_first_nodes(self, id):
#   nodes = []
#   stack = [id]
#   while stack:
#     cur_node = stack[0]
#     stack = stack[1:]
#     nodes.append(cur_node)
#     for child in reversed(tree[cur_node]["children"]):  # .get_rev_children():
#       stack.insert(0, child)
#   return nodes
#
#
# def walkBreathFirstFnc(tree, id):
#   # BFS(v)
#   #   let neighbours be the set of all  neighbours of  vertex  v
#   #   for neighbor in neighbors:
#   #     if neighbor is not visited:
#   #       visit neighbour
#   #   for neighbor in neighbors:
#   #     recurisvely call BFS(neighbor)
#   nodes = []
#   stack = [id]
#   while stack:
#     cur_node = stack[0]
#     stack = stack[1:]
#     nodes.append(cur_node)
#     for child in tree[cur_node]["children"]:  # cur_node.get_children():
#       stack.append(child)
#   return nodes


class ObjectTreeNonUniqueTags(dict):
  """
  requires unique tags
  """

  def __init__(self, root):
    """
    starts a tagged tree
    :param root: name of the root -- string
    """
    super().__init__()
    _nodeID = 0
    self["tree"] = Tree(_nodeID)
    self["nodes"] = {
            _nodeID: root
            }
    self["IDs"] = {
            root: _nodeID
            }

  def addChildtoNode(self, child, parent):
    """
    add a child tag to the tree
    :param child: tag of child
    :param parent: tag of parent
    :return:
    """
    id_parent = self["IDs"][parent]
    i = self["tree"].addChild(id_parent)
    self["nodes"][i] = child
    self["IDs"][child] = i

  def getLeaves(self, node_ID_or_tag):
    """

    :param node_ID_or_tag: either node as ID (integer) or node as tag (string)
    :return: leave_tags, leave_IDs  both tags and IDs
    """
    # TODO: incosistent change to node_tag
    dummy = 'dummy'
    if isinstance(node_ID_or_tag, dummy.__class__):
      node_ID = self["IDs"](node_ID_or_tag)
    else:
      node_ID = node_ID_or_tag
    leave_tags = []
    leave_IDs = []
    for i in self["tree"].walkDepthFirst(node_ID):

      if self["tree"].isLeave(i):
        leave_tags.append(self["nodes"][i])
        leave_IDs.append(i)
        # print(i, '  -  ', l)

    return leave_tags, leave_IDs

  def rename(self,ID, new_tag):

    old_tag = self["nodes"][ID]
    self["nodes"][ID] = new_tag
    if old_tag in self["IDs"]:
      del self["IDs"][old_tag]
    self["IDs"][new_tag] = ID
    # for id in self["nodes"]:
    #   tag = self["nodes"][id]
    #   if tag == new_tag:
    #     print("found a tag", tag)
    #     self["nodes"][id] = new_tag


  def makeTaggedTree(self):
    taggedTree = {}
    for i in self["tree"].walkDepthFirst(0):
      children = []
      [children.append(self["nodes"][child]) for child in self["tree"][i]["children"]]
      ancestors = []
      [ancestors.append(self["nodes"][ancestor]) for ancestor in self["tree"][i]["ancestors"]]

      taggedTree[self["nodes"][i]] = {}
      taggedTree[self["nodes"][i]]["children"] = children
      taggedTree[self["nodes"][i]]["ancestors"] = ancestors
    return taggedTree




class ObjectTreeUniqueTags(dict):
  """
  requires unique tags
  """

  def __init__(self, root):
    """
    starts a tagged tree
    :param root: name of the root -- string
    """
    super().__init__()
    _nodeID = 0
    self["tree"] = Tree(_nodeID)
    self["nodes"] = {
            _nodeID: root
            }
    self["IDs"] = {
            root: _nodeID
            }

  def addChildtoNode(self, child, parent):
    """
    add a child tag to the tree
    :param child: tag of child
    :param parent: tag of parent
    :return: 
    """
    id_parent = self["IDs"][parent]
    i = self["tree"].addChild(id_parent)
    self["nodes"][i] = child
    self["IDs"][child] = i

  def getLeaves(self, node_ID_or_tag):
    """

    :param node_ID_or_tag: either node as ID (integer) or node as tag (string)
    :return: leave_tags, leave_IDs  both tags and IDs
    """
    # TODO: incosistent change to node_tag
    dummy = 'dummy'
    if isinstance(node_ID_or_tag, dummy.__class__):
      node_ID = self["IDs"](node_ID_or_tag)
    else:
      node_ID = node_ID_or_tag
    leave_tags = []
    leave_IDs = []
    for i in self["tree"].walkDepthFirst(node_ID):

      if self["tree"].isLeave(i):
        leave_tags.append(self["nodes"][i])
        leave_IDs.append(i)
        # print(i, '  -  ', l)

    return leave_tags, leave_IDs

  def getChildren(self, node_tag):
    children_tags = []
    id = self["IDs"][node_tag]
    for child_id in self["tree"].getChildren(id):
      child_tag = self["nodes"][child_id]
      children_tags.append(child_tag)
    return children_tags

  def getAncestors(self, node_tag):
    ancestor_tags = []
    for i in self["tree"].getAncestors(self["IDs"][node_tag]):
      ancestor_tags.append(self["nodes"][i])
    return ancestor_tags

  def getCommonAncestor(self, node1, node2):
    inverted = invertDict((self["nodes"]))
    r = self["tree"].getCommonAncestor(inverted[node1], inverted[node2])
    return self["nodes"][r]

  def makeTaggedTree(self):
    taggedTree = {}
    for i in self["tree"].walkDepthFirst(0):
      children = []
      [children.append(self["nodes"][child]) for child in self["tree"][i]["children"]]
      ancestors = []
      [ancestors.append(self["nodes"][ancestor]) for ancestor in self["tree"][i]["ancestors"]]

      taggedTree[self["nodes"][i]] = {}
      taggedTree[self["nodes"][i]]["children"] = children
      taggedTree[self["nodes"][i]]["ancestors"] = ancestors
    return taggedTree


class Tree(dict):
  ''' a tree of identifiers
      stored in a dictionaries that are of the form
      node_id = {'parent': [father, grandfather, .... , root]
                 'children': [child 1, child2, ... ]
                 }
      '''

  def __init__(self, root=0):
    dict.__init__(self)
    self.root = root
    self.currentID = root
    self[root] = {
            'ancestors': [],
            'children' : []
            }

  def imposeIDTree(self, IDtree):
    nodes = list(IDtree.keys())
    m = max(nodes)
    self = IDtree
    self.currentID = m
    self.__redoMap()

    # nodes = list(self.keys())
    # m = max(nodes)
    # self.currentID = m
    # self.__redoMap()

  #
  #
  def __redoMap(self):
    self.map = dict([(i, i) for i in self.keys()])

  def getLastID(self):
    a = self.currentID
    return a

  def addChild(self, the_parentID):
    #        print 'add to id', the_parentID
    self.currentID = self.currentID + 1
    the_ID = self.currentID
    self[the_ID] = {
            'ancestors': [],
            'children' : []
            }
    self[the_parentID]['children'].append(the_ID)
    self[the_ID]['ancestors'].append(the_parentID)
    self[the_ID]['ancestors'].extend(self[the_parentID]['ancestors'][:])
    return the_ID

  def addTree(self, rooted_tree, parentID):

    offset = max(self.keys()) + 1
    map = rooted_tree.mapMe(offset)
    self.addMappedTree(rooted_tree, parentID)
    return map

  def addMappedTree(self, mapped_tree, the_parentID):
    mapped_nodes = mapped_tree.getNodes()
    root_mapped_tree = mapped_tree.getRoot()
    self[the_parentID]['children'].append(root_mapped_tree)
    self.update(mapped_tree)
    ancestors = [the_parentID]
    ancestors.extend(self[the_parentID]['ancestors'])
    for i in mapped_nodes:
      self[i]['ancestors'].extend(ancestors)
    self.currentID = max(self)

  def removeID(self, the_ID):
    self._removefromParent(the_ID)
    del self[the_ID]

  def _removefromParent(self, the_ID):
    the_parentID = self[the_ID]['ancestors'][0]
    i = self[the_parentID]['children'].index(the_ID)
    del self[the_parentID]['children'][i]

  def moveID(self, what_ID, to_ID):
    for i in self.walkDepthFirst(what_ID):
      if i == to_ID:
        print('tree >>> cannot move')
        return False
    p_what = self[what_ID]['ancestors']
    n_what = len(p_what)
    p_to = self[to_ID]['ancestors']
    self._removefromParent(what_ID)
    self[to_ID]['children'].append(what_ID)
    self._swapParents(what_ID, n_what, [to_ID] + p_to)
    return True

  def _swapParents(self, ID, n_what, p_to):
    self[ID]['ancestors'] = self[ID]['ancestors'][0:-n_what] + p_to
    [self._swapParents(i, n_what, p_to) for i in self[ID]['children']]

  def getImmediateParent(self, id):
    ''' this is the immediate parent'''
    a = self.getAncestors(id)
    if a != []:
      return self.getAncestors(id)[0]
    else:
      return None

  def getAncestors(self, id):
    """ these are the parents """
    a = self[id]['ancestors']
    return a

  def getCommonAncestor(self, id1, id2):
    if id1 == self.root:
      return None
    if id2 == self.root:
      return None
    anchestors1 = list(reversed(self.getAncestors(id1)))
    anchestors2 = list(reversed(self.getAncestors(id2)))
    r = 0
    l1 = len(anchestors1) - 1
    l2 = len(anchestors2) - 1
    for i in range(min(l1, l2)):
      if anchestors1[i] != anchestors2[i]:
        return r
      else:
        r += 1
    return r

  def getCommonAncestorNode(self, id1, id2):
    if id1 == self.root:
      return None
    if id2 == self.root:
      return None
    anchestors1 = list(reversed(self.getAncestors(id1)))
    anchestors2 = list(reversed(self.getAncestors(id2)))
    l1 = len(anchestors1)
    l2 = len(anchestors2)
    last = 0
    for i in range(min(l1, l2)):
      if anchestors1[i] != anchestors2[i]:
        return last
      else:
        last = anchestors1[i]
    return last

  def getFirstCommonNode(self, id1, id2):
    if id1 == self.root:
      path1 = [self.root]
    else:
      path1 = list(reversed(self.getAncestors(id1))) + [id1]
    if id2 == self.root:
      path2 = [self.root]
    else:
      path2 = list(reversed(self.getAncestors(id2))) + [id2]
    # print("getFirstCommonNode", path1, path2)
    l1 = len(path1)
    l2 = len(path2)
    last = 0
    for i in range(min(l1, l2)):
      if path1[i] != path2[i]:
        return last
      else:
        last = path1[i]
    return last

  def getNodes(self):
    a = list(self.keys())
    return a

  def getRoot(self):
    nodes = self.getNodes()
    for i in nodes:
      if self.isRoot(i):
        return i

  def getAllInternalNodes(self):
    internal_node = []
    for node in list(self.keys()):
      if not self.isLeave(node):
        internal_node.append(node)
    return internal_node

  def getAllLeaveNodes(self):
    s_nodes = set(self.getNodes())
    s_internal = set(self.getAllInternalNodes())
    s_leaves = s_nodes - s_internal
    return list(s_leaves)

  def extractSubTreeAndMap(self, nodeID):

    branch = {}
    parents = self.getAncestors(nodeID)
    for i in self.walkDepthFirst(nodeID):
      id = i
      branch[id] = {
              'ancestors': [],
              'children' : []
              }
      branch[id]['ancestors'].extend(copy.copy(self[id]['ancestors']))
      branch[id]['children'].extend(copy.copy(self[id]['children']))
      for k in parents:
        branch[id]['ancestors'].remove(k)
    branch[nodeID] = {
            'ancestors': [],
            'children' : []
            }
    branch[nodeID]['ancestors'].extend([])
    branch[nodeID]['children'].extend(copy.copy(self[nodeID]['children']))

    tree = Tree(nodeID)
    tree.update(branch)
    map = tree.mapMe()

    return tree, map

  def getChildren(self, id):
    ''' these are the children '''
    return self[id]['children']

  def getSiblings(self, id):
    ''' these are the siblings -- as a copy'''
    parentID = self.getImmediateParent(id)
    if parentID == None:
      return []
    else:
      children = self.getChildren(parentID)
      siblings = []
      i = children.index(id)
      return children[:i] + children[i + 1:]

  def getMappedSubtree(self, id):
    nodes = self.walkDepthFirst(id)
    new_tree = Tree(root=id)
    # map = {}
    # count = 0
    for nodeID in nodes:
      # map[nodeID] = count
      new_tree[nodeID] = copy.deepcopy(self[nodeID])
      new_tree[nodeID]["ancestors"].remove(0)
      # count += 1
    node_map =  new_tree.mapMe()
    return new_tree, node_map


  def isRoot(self, id):
    if self[id]['ancestors'] == []:
      return True
    else:
      return False

  def isLeave(self, id):
    if self[id]['children'] == []:
      return True
    else:
      return False

  def walkDepthFirst(self, id):
    #   for child in self[id]['children']:
    #     if self[child]['children'] == []:
    #       #                print child, 'is a leave'
    #       yield child, 'leave'
    #     else:
    #       yield child, 'node'
    #       for x in self.walkDepthFirst(child):
    #         self.walkDepthFirst(x)
    #         #                    print 'walk' , x, '    kids ', self[x]['children']
    #         yield x
    #
    # def get_depth_first_nodes(self, id):
    nodes = []
    stack = [id]
    while stack:
      cur_node = stack[0]
      stack = stack[1:]
      nodes.append(cur_node)
      for child in reversed(self[cur_node]["children"]):  # .get_rev_children():
        stack.insert(0, child)
    return nodes

  def walkBreathFirst(self, id):
    # BFS(v)
    #   let neighbours be the set of all  neighbours of  vertex  v
    #   for neighbor in neighbors:
    #     if neighbor is not visited:
    #       visit neighbour
    #   for neighbor in neighbors:
    #     recurisvely call BFS(neighbor)
    nodes = []
    stack = [id]
    while stack:
      cur_node = stack[0]
      stack = stack[1:]
      nodes.append(cur_node)
      for child in self[cur_node]["children"]:  # cur_node.get_children():
        stack.append(child)
    return nodes

  def mapMe(self, offset=0):
    old_nodes = self.walkBreathFirst(self.root)
    map = dict([(old_nodes[i], i + offset) for i in range(len(old_nodes))])
    new = {}
    for n in old_nodes:
      nn = map[n]
      new[nn] = {}
      new[nn]["ancestors"] = [map[a] for a in self[n]["ancestors"]]
      new[nn]["children"] = [map[a] for a in self[n]["children"]]

    for n in old_nodes:
      del self[n]

    self.update(new)
    self.root = offset
    self.currentID = max(self)

    return map

    #        print 'tree map', self
    #        print '........', map
    # a = {}
    # nodes = self.getNodes()
    # for i in nodes:
    #   k = map[i]
    #   a[k] = {'ancestors': [], 'children': []}
    #   no_parents = len(self[i]['ancestors'])
    #   if no_parents > 0:
    #     for j in range(no_parents):
    #       a[k]['ancestors'].append(map[self[i]['ancestors'][j]])
    #   else:
    #     root = k
    #   no_children = len(self[i]['children'])
    #   if no_children > 0:
    #     for j in range(no_children):
    #       #                    print j
    #       a[k]['children'].append(map[self[i]['children'][j]])
    # for i in nodes:
    #   if i not in a:
    #     del self[i]
    # self.update(a)
    # return self

  def toJson(self):
    json = {}
    for hash in self:
      json[(hash)] = self[hash]

    return json

  def fromJson(self, json):
    for hash in json:
      self[int(hash)] = json[hash]

  def printMe(self):

    template = "\tn: %s \ta: %s \t        c: %s"
    for i in sorted(self.walkDepthFirst(self.root)):
      ancestors = self[i]['ancestors']
      children = self[i]['children']
      print(template % (i, ancestors, children))

  def write(self, f, ID):
    f.write('>>> begin tree:')
    f.write(' root | nodeIDs | { (id, ancestors, children},\n')
    f.write(str(self.root) + '\n')
    f.write(str(list(self.keys())) + '\n')
    line = str((ID, self[ID]['ancestors'], self[ID]['children'])) + '\n'
    f.write(line)
    for i in self.walkDepthFirst(ID):
      id = i[0]
      line = str((id, self[id]['ancestors'], self[id]['children']))
      f.write(line)
      f.write('\n')
    f.write('end tree <<<\n')

  def read(self, f, dummy):
    # re-creates itself
    # dummy argument added to enable automation of write - read
    line = f.readline()  # start
    line = f.readline()  # root
    root = eval(line)
    #        print root
    self.__init__(root)
    line = f.readline()  # node ID s
    nodeIDs = eval(line)
    for id in nodeIDs:
      line = f.readline()
      i, A, C = eval(line)
      self[i] = {
              'ancestors': A,
              'children' : C
              }
    # print self[i]
    line = f.readline()
    if line[:12] != 'end tree <<<':
      print(('Tree.read: reading error', line))
    nodeIDs.sort()
    self.currentID = nodeIDs[-1]
    return self

  def fix(self):
    for id in self.getNodes():
      try:
        print(('try :', self[id]))
        self[id].update({
                'ancestors': self[id]['parents']
                })
        del self[id]['parents']
        print(('fixed :', id, self[id]))
      except:
        print(('fix : no action', id, self[id]))

  def getBareTree(self):
    bare_tree = [self[i] for i in self]
    return bare_tree


# #testing
#
if __name__ == '__main__':
  nodeID = 0  # -1 # ID(-1)  # setup object node ID
  #
  tree = Tree(nodeID)

  print(1), tree.printMe()

  id = tree.addChild(nodeID)
  print(2)
  tree.printMe()

  id = tree.addChild(nodeID)
  print(3)
  tree.printMe()

  tree.removeID(1)
  print(4)
  tree.printMe()

  id = tree.addChild(nodeID)
  print(5)
  tree.printMe()

  id = tree.addChild(nodeID)
  print(7)
  tree.printMe()

  id = tree.addChild(3)
  print(8)
  tree.printMe()

  id = tree.addChild(5)
  print(9)
  tree.printMe()

  id = tree.addChild(3)
  print(10)
  tree.printMe()

  tree.moveID(3, 2)
  print(11)
  tree.printMe()

  tree.moveID(3, 4)
  print(12)
  tree.printMe()

  print(13)
  c, map = tree.extractSubTreeAndMap(3)
  print('map: ', map)
  c.printMe()

  print(14)
  tree.printMe()
  nodes = tree.walkBreathFirst(0)
  print('walk_breath_first nodes ', nodes)

  nodes = tree.walkDepthFirst(0)
  print('walk_depth_first nodes ', nodes)

  print(15)
  tree.mapMe()
  tree.printMe()

  map = tree.addTree(c, 0)
  print(16)
  print('map: ', map)
  tree.printMe()
  tree.mapMe()
  tree.printMe()

  g = ObjectTreeUniqueTags('ontology')
  g.addChildtoNode('physical', 'ontology')
  g.addChildtoNode('solid', 'physical')
  g.addChildtoNode('phasea', 'solid')
  g.addChildtoNode('phaseb', 'solid')
  g.addChildtoNode('phasec', 'solid')
  g.addChildtoNode('liquid', 'physical')
  g.addChildtoNode('solid', 'physical')
  g.addChildtoNode('solid', 'gas')
  g.addChildtoNode('information', 'ontology')
  g.addChildtoNode('discrete','information')
  g.addChildtoNode('continuous','information')

  g.tree.printMe()

  tags, IDs = g.getLeaves(0)
  print(tags)

  for i in tags:
    ancestor_tags = g.getAncestors(i)
    print((i, ' - ', ancestor_tags))
