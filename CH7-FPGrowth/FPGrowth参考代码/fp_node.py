class FPNode(object):
    '''A NODE IN AN FP TREE'''
    ''' FP树的节点类'''    

    def __init__(self, tree, item, count=1):
        self._tree = tree #节点所属的树
        self._item = item #节点对应的item的标号
        self._count = count #通过节点的路径的个数（对树的根节点，总为None）
        self._parent = None #节点的父节点（对树的根节点，总为None）
        self._children = {} # 包含各子节点的字典
        self._neighbour = None # 链接的下一个节点（用于每个item节点链表的跟踪指针）

    def __repr__(self):
        if self.root:
            return '<%s (root)>' % type(self).__name__
        return '<%s %r (%r)>' % (type(self).__name__, self.item, self.count)


    def add(self, child):
        '''ADDS GIVEN NODE AS A CHILD OF THE CURRENT NODE'''
        ''' 添加一个子节点 '''
        
        if not isinstance(child, FPNode):
            raise TypeError("ERROR: CHILD TO BE ADDED MUST BE FPNode")
        
        if not child.item in self._children: #如果尚不存在该标号的子节点才添加
            self._children[child.item] = child #创建新节点
            child.parent = self #设置新节点的父节点为本节点

    def search(self, item):
        '''CHECKS IF CURRENT NODE HAS A CHILD NODE FOR THE GIVEN ITEM'''
        ''' 在子节点字典中搜索一个特定项标号的节点并返回'''
        
        try:
            return self._children[item]
        except KeyError:
            return None

    def remove(self, child):
        '''REMOVES CHILD NODE FROM CHILDREN OF CURRENT NODE'''
        ''' 删除指定的子节点 '''
        
        try:
            if self._children[child.item] is child:
                del self._children[child.item] #从字典中删除
                child.parent = None #设置被删除的子节点父节点为空
                self._tree._removed(child) #同时从item链中删除该节点
                for sub_child in child.children: #处理被删除子节点的各个子节点，将其转移到当前节点中
                    try:
                        self._children[sub_child.item]._count += sub_child.count #如果该节点标号在当前节点的子节点中存在，直接将其Count加到当前节点的子节点里
                        sub_child.parent = None #节点父节点置空
                    except KeyError:
                        self.add(sub_child) #否则，将该节点添加为当前节点的子节点
                child._children = {} #清空被删除子节点的子节点字典
            else:
                raise ValueError('ERROR: CHILD TO BE REMOVED IS NOT THE CHILD OF THIS NODE')
        except:
            raise ValueError('ERROR: CHILD TO BE REMOVED IS NOT THE CHILD OF THIS NODE')

    def __contains__(self, item):
        ''' 是否包含特定项标号的子节点'''
        return item in self._children 

    @property
    def tree(self):
        '''RETURNS THE TREE TO WHICH CURRENT NODE BELONGS'''
        ''' 返回所属的树'''
        return self._tree 

    @property
    def item(self):
        '''RETURNS ITEM CONTAINED IN CURRENT NODE'''
        ''' 返回对应的项标号'''
        return self._item 

    @property
    def count(self):
        '''RETURNS THE COUNT OF CURRENT NODE\'S ITEM'''
        ''' 返回经过节点的路径条数'''
        return self._count 

    def increment(self):
        '''INCREMENTS THE COUNT OF CURRENT NODE\'S ITEM'''
        ''' 路径条数+1'''
        if self._count is None:
            raise ValueError('ERROR: ROOT NODE HAS NO COUNT')
        self._count += 1 
    
    @property
    def root(self):
        '''CHECKS IF CURRENT NODE IS ROOT OF THE FP TREE'''
        ''' 是否是一个根节点'''
        return self._item is None and self._count is None

    @property
    def leaf(self):
        '''CHECKS IF CURRENT NODE IS NODE OF THE FP TREE'''
        ''' 是否是一个叶子节点'''
        return len(self._children) == 0 

    def parent():
        ''' 父节点获取或设置'''
        def fget(self):
            return self._parent
        def fset(self, value):
            if value is not None and not isinstance(value, FPNode):
                raise TypeError('ERROR: A NODE MUST HAVE AN FP NODE AS A PARENT')
            if value and value.tree is not self.tree:
                raise ValueError('ERROR: NODE OF ONE TREE CANNOT HAVE PARENT FROM ANOTHER TREE')
            self._parent = value
        return locals()
    parent = property(**parent()) 

    def neighbour():
        ''' 链接的下一个节点的获取和设置'''
        def fget(self):
            return self._neighbour
        def fset(self, value):
            if value is not None and not isinstance(value, FPNode):
                raise TypeError('ERROR: A NODE MUST HAVE AN FP NODE AS A NEIGHBOUR')
            if value and value.tree is not self.tree:
                raise ValueError('ERROR: NODE OF ONE TREE CANNOT HAVE NEIGHBOUR FROM ANOTHER TREE')
            self._neighbour = value
        return locals()
    neighbour = property(**neighbour())
                
    @property
    def children(self):
        '''RETURNS CHILDREN OF CURRENT NODE'''
        ''' 返回所有子节点构成的元组'''
        return tuple(self._children.values())

    def inspect(self, depth=0):
        ''' 节点输出（控制台）'''
        print('   ' * depth + repr(self))
        for child in self.children:
            child.inspect(depth + 1)
