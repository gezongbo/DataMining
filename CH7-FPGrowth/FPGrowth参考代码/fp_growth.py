import csv
from collections import defaultdict, namedtuple
from optparse import OptionParser

from fp_node import FPNode
from fp_tree import FPTree


def conditional_tree_from_paths(paths, minimum_support):
    """Builds a conditional FP-tree from the given prefix paths."""
    ''' 使用一个项标号对应的所有追溯路径建立该项标号的一个条件FP树'''
    tree = FPTree() #初始化
    condition_item = None #要为其建立条件FP树的项标号
    items = set() #路径（树）中涉及到的所有项标号

    for path in paths: #将每个路径添加到FP树中
        if condition_item is None:
            condition_item = path[-1].item #将路径中的最后一个项标号作为要为其建立条件FP树的项标号

        point = tree.root #从根节点开始（其是起始父节点）
        for node in path:
            next_point = point.search(node.item) 
            if not next_point: #若父节点中不存在该标号的子节点
                items.add(node.item)  #记录新出现的项标号
                count = node.count if node.item == condition_item else 0 #除了要为其建立条件FP数的项标号对应的节点（其Count来自原始FP树，其他节点Count都先设置为0，下面再计算）
                next_point = FPNode(tree, node.item, count) #建立一个新的FPNode
                point.add(next_point) #将其添加为父节点的子节点
                tree._update_route(next_point) #将其添加到对应项标号的链表中
            point = next_point #下移一层，继续处理路径的下一个节点

    assert condition_item is not None

    ''' 计算除了condition_item标号以外节点的Count（通过路径数）'''
    for path in tree.prefix_paths(condition_item): #在刚建立的条件FP树上，找出以condition_item结尾的所有路径
        count = path[-1].count #对每条路径，取出其最后一个节点（其实就是路径最后的condition_item标号的节点）的count
        for node in reversed(path[:-1]):
            node._count += count  #将路径上所有节点的count用最后一个节点(condition_item标号的节点)的count修正

    ''' 计算每个涉及的项标号的支持度，如果小于阈值，将其所有节点从树中剪掉（注意要处理被剪掉节点子树上的count）'''
    for item in items:
        support = sum(n.count for n in tree.nodes(item))
        if support < minimum_support:
            # Doesn't make the cut anymore
            for node in tree.nodes(item):
                if node.parent is not None:
                    node.parent.remove(node)
                    
    ''' 删除每条路径的最后一个节点（也就是condition_item标号的节点），这样以其为最后节点的所有路径的条件子树就构建起来了'''
    for node in tree.nodes(condition_item):
        if node.parent is not None:
            node.parent.remove(node)

    return tree

def find_frequent_itemsets(transactions, minimum_support, include_support=False):
    '''FINDS FREQUENT ITEMSETS IN THE GIVEN TRANSACTIONS'''
    ''' 计算频繁集'''
    
    items = defaultdict(lambda:0) #每个（经过预处理后）项标号对应的支持度字典（1-项集的支持度字典）
    processed_transactions = [] #保存预处理后获取的事务集

    ''' 可以预处理下事务集，比如删除某些项编号，排除某些事务等，这里未做任何处理'''
    for transaction in transactions:        
        transaction = transaction #transaction[0].split()                   
        processed = []
        for item in transaction:
            items[item] += 1
            processed.append(item)
        processed_transactions.append(processed)
  
    items = dict((item, support) for item, support in items.items()
                  if support >= minimum_support) #用阈值筛选出频繁的1-项集

    def clean_transaction(transaction):
        '''STRIPS TRANSACTIONS OF INFREQUENT ITEMS AND SURVIVING ITEMS ARE SORTED IN DECREASING ORDER OF FREQUENCY'''
        ''' 按照预处理的结果，自每个事务中删除已经排除的项标号，同时将事务中的每个项标号按照其支持度大小排序（这样构造FP树后，支持度低的都在树的底层，便于修剪'''
        transaction = list(filter(lambda v: v in items, transaction))         
        transaction.sort(key=lambda v: items[v], reverse=True)        
        return transaction

    ''' 构建FP树'''
    master = FPTree()
    for transaction in map(clean_transaction, processed_transactions): #对数据进行预处理
        master.add(transaction) #将事务（路径）逐个添加到FP树
    # master.inspect()

    def find_with_suffix(tree, suffix):
        ''' 后缀法沿树逐层向上寻找频繁项集（注意，这里第一次用的是原始FP树，下层递归就都是用的重新构建的条件FP树了）'''
        for item, nodes in tree.items(): #对每个项标号处理（注意由于建立FP树时，事务中都是支持度高的项在前面，会优先处理支持度高的项标号）
            support = sum(n.count for n in nodes) #计算该项标号的支持度
            if support >= minimum_support: #如果满足支持度阈值，找到一个频繁集
                found_set = [item] + suffix
                yield (found_set, support) if include_support else found_set

                '''Build a conditional tree and recursively search for frequent itemsets within it.'''
                ''' 从该标号对应的节点继续向上追溯，找出所有路径，构造条件FP树'''
                cond_tree = conditional_tree_from_paths(tree.prefix_paths(item),
                    minimum_support)
                ''' 在条件FP树上继续寻找频繁的前缀路径'''
                for found_suffix in find_with_suffix(cond_tree, found_set):
                    yield found_suffix

    '''Search for frequent itemsets, and yield the results we find.'''
    ''' 搜索频繁集并返回迭代器'''
    for itemset in find_with_suffix(master, []):
        yield itemset

if __name__ == '__main__':
    data = []
    with open('data/transaction.csv','r') as csvf:
        lines = csv.reader(csvf)
        data = list(lines)    
    minsup = 2
    ffi = find_frequent_itemsets(data, minsup, True)    
    for itemset, support in ffi:
        print('{' + ', '.join(itemset) + '} ' + str(support))
