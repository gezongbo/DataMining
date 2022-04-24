from collections import namedtuple
from fp_node import FPNode

class FPTree(object):
    '''FP TREE STRUCTURE'''
    ''' FP树结构类'''
    Route = namedtuple('Route', 'head tail') #一个简化类（命名元组），用于描述每个项标号所有的FPNode的链表，其实同时包含头尾两个FPNode的引用，通过FPNode的neibour指针遍历获取所有FPNode

    def __init__(self):
        ''' 初始化根节点和各项标号链表使用的字典 '''
        self._root = FPNode(self, None, None) #根节点
        self._routes = {} #以项标号为key，包含每个项的FP节点列表（其实是上面的命名元组，仅包含头尾两个FPNode）

    @property
    def root(self):
        '''RETURNS ROOT OF THE FP TREE'''
        ''' 返回根节点'''
        return self._root

    def add(self, transaction):
        '''ADDS A TRANSACTION TO THE TREE'''
        ''' 向树中添加一个事务（或一条路径）'''
        point = self._root #从根节点开始
        for item in transaction: #按事务中的项排序沿树逐层向下查找
            next_point = point.search(item) 
            if next_point: #父节点的子节点字典中以前已经建立了该项标号的子节点 
                next_point.increment() #直接给找到的子节点计数+1
            else:
                next_point = FPNode(self, item) #否则新建一个节点（count默认为1）
                point.add(next_point) #添加为父节点的一个子节点
                self._update_route(next_point) #添加到相应项标号的节点链表中
            point = next_point #向下移动到当前节点，继续处理下一层的节点

    def _update_route(self, point):
        '''ADD THE NODE POINT TO THE ROUTE THROUGH ALL NODES FOR ITS ITEM'''
        ''' 将新建节点添加到对应项标号的节点列表中'''
        assert self is point.tree

        try:
            route = self._routes[point.item] #如果项标号对应的列表已经存在（建立过）
            route[1].neighbour = point #将新节点链接到尾节点（作为尾节点的下一个）
            self._routes[point.item] = self.Route(route[0], point) #修正尾节点为刚添加的节点 
        except KeyError:
            self._routes[point.item] = self.Route(point, point) #如果没有建立过，新建项编号的链表，首尾节点引用都是当前添加的节点

    def items(self):
        '''GENERATE 2-TUPLES FOR EACH ITEM OF THE FORM (ITEM, GENERATOR)'''
        ''' 返回一个迭代器，提供项标号和其所有FPNode的迭代器'''
        for item in self._routes:
            yield(item, self.nodes(item))

    def nodes(self, item):
        '''GENERATES THE SEQUENCE OF NODES THAT CONTAIN THE GIVEN ITEM'''
        ''' 对于给定的项标号，返回一个枚举其所有FPNode的迭代器'''
        try:
            node = self._routes[item][0]
        except KeyError:
            return
        while node:
            yield node
            node = node.neighbour

    def prefix_paths(self, item):
        '''GENERATES PREFIX PATHS ENDING WITH CURRENT ITEM'''
        ''' 给定一个类标号，返回所有以该标号结尾的路径（该操作用于获取构造针对特定项标号的条件FP树所需要的所有路径）'''

        def collect_path(node):
            ''' 从给定的node向上追溯到树的根，返回追溯获取的路径'''
            path = []
            while node and not node.root:
                path.append(node)
                node = node.parent
            path.reverse()
            return path

        return (collect_path(node) for node in self.nodes(item))

    def inspect(self):
        ''' 输出树（控制台），包括树结构和各项标号及其所有FPNode'''
        print('\nTREE:')
        self.root.inspect(1)
        print('\nROUTES:')
        for item, nodes in self.items():
            print('%r' % item)
            for node in nodes:
                print('%r' % node)

    def _removed(self, node_to_remove):
        '''PERFORMS CLEANUP DURING REMOVAL OF A NODE'''
        ''' 自项标号链表中删除一个节点'''
        head, tail = self._routes[node_to_remove.item] #获取链表的首节点和尾节点
        if node_to_remove is head: #如果要删除的节点是首节点
            if node_to_remove is tail or not node_to_remove.neighbour: #如果只有一个节点
                # It was the sole node.
                del self._routes[node_to_remove.item] #直接从字典中删除该项标号及其链表
            else:
                self._routes[node_to_remove.item] = self.Route(node_to_remove.neighbour, tail) #否则修正命名元组中的首节点
        else: #如果要删除的不是首节点
            for node in self.nodes(node_to_remove.item):
                if node.neighbour is node_to_remove: #找到其前一个节点
                    node.neighbour = node_to_remove.neighbour # skip over #修改前一个节点的neibour指针
                    if node_to_remove is tail: 
                        self._routes[node_to_remove.item] = self.Route(head, node) #如果删除的是尾节点，修正命名元组中的尾节点
                    break
