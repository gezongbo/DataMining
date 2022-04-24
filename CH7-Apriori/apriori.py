import argparse
from itertools import chain, combinations

class Rule(object):
    '''ASSOCIATION RULES'''
    '''一个规则类，成员包含规则前件A，后件B，规则的支持度，置信度，time是规则的序号，无意义'''
    def __init__(self, A, B, support, confidence, time):
        self.A = A
        self.B = B
        self.support = support
        self.confidence = confidence
        self.time = time

    def __repr__(self):
        return '%s ==> %-6s\t%.3f\t%.3f' % (' '.join(sorted(list(self.A))),
                                        ' '.join(sorted(list(self.B))),
                                        self.confidence,
                                        self.support)

class Apriori(object):
    '''APRIORI'''
    '''初始化，设定数据集，支持度阈值，置信度阈值，同时计算出频繁集'''
    def __init__(self, data, min_support, min_confidence):
        self.data = data
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.itemset, self.transaction_list = self.get_itemset_from_data()
        self.frequent_itemset = self.get_frequent_itemset()

    @staticmethod
    def join_set(itemset, k):
        '''JOINS TWO ITEMSETS TO GET A k LENGTH UNION'''
        '''使用两个k-1阶频繁子集生成k阶候选集，这里简单使用了union方法，效率低，有重复，可优化'''
        return set([i.union(j) for i in itemset for j in itemset if len(i.union(j)) == k])

    @staticmethod
    def get_combined_subsets(itemset):
        '''COMBINES ITEMSETS'''
        ''' 这里用于生成频繁集所有可能的子集，构造规则的时候使用，这里也可以剪枝优化 '''
        return chain(*[combinations(itemset, index + 1) for index, item in enumerate(itemset)])

    def get_itemset_from_data(self):
        '''EXTRACTS ITEMSET FROM DATABASE'''
        ''' 这里使用set找出了所有的可能项（顺便也构造了1-项集），同时构造出了事务集列表'''
        itemset = set()
        transaction_list = list()
        for row in self.data:
            transaction_list.append(frozenset(row))
            for item in row:
                if item:
                    itemset.add(frozenset([item]))
        return itemset, transaction_list

    def get_support_list(self):
        '''GENERATES SUPPORT LIST HIGHER THAN MINIMUM SUPPORT THRESHOLD'''
        ''' 这里计算当前k-项集的支持度，并使用支持度阈值进行筛选，判断一个事务是否支持项集直接使用了issubset方法，这里也可以进行优化'''
        unpruned_list = [(item, float(sum(1 for row in self.transaction_list if item.issubset(row)))/len(self.transaction_list))
                         for item in self.itemset]
        return dict([(item, support) for item, support in unpruned_list if support >= self.min_support])

    
    def get_frequent_itemset(self):
        '''GENERATES FREQUENT ITEMSETS'''
        ''' 计算所有频繁项集 '''
        ''' 这种处理方式没有通过字典序要求合并k-1阶项集来避免生成重复的k阶项集，也没有使用k-1阶频繁集筛选k阶频繁集！！！！！'''
        frequent_itemset = dict()
        k = 1
        while True:
            ''' 当k=1时，直接用get_itemset_from_data中构造的1-项集计算支持度同时用阈值筛选 '''
            ''' 当k>1时，用上次获得的k-1-项集组合生成k-项集，再计算其支持度并用阈值筛选'''
            if k > 1:
                self.itemset = self.join_set(next_itemset, k)
            next_itemset = self.get_support_list()
            ''' 如果所有的候选都被阈值筛选掉了，结束 '''
            if not next_itemset:
                break
            ''' 记录找到的频繁集，前面k-1阶合并得到k阶进行了所有可能的合并，所有有重复，这里使用update方法去掉重复 '''            
            frequent_itemset.update(next_itemset)
            k += 1
        return frequent_itemset

    def run(self):
        '''RUNS APRIORI ALGORITHM'''
        ''' 针对每个频繁集，构建可能规则集并计算置信度进行筛选 '''
        ''' 这里构造了所有可能的规则进行置信度筛选，没有使用反单调性进行剪枝，可优化！！！！！！！！'''
        rules, time = list(), 0
        for item, support in self.frequent_itemset.items(): #对所有的频繁集进行枚举
            if len(item) > 1:
                for A in self.get_combined_subsets(item): #对所有可能子集进行枚举
                    B = item.difference(A) #后件
                    if B:
                        A = frozenset(A)
                        AB = A | B
                        confidence = float(self.frequent_itemset[AB]) / self.frequent_itemset[A]
                        if confidence >= self.min_confidence:
                            rules.append(Rule(A, B, support=self.frequent_itemset[AB], confidence=confidence, time=time))
                            time += 1
        return rules, self.frequent_itemset

def parse_arguments():
    '''PARSES COMMAND LINE ARGUMENTS'''
    argparser = argparse.ArgumentParser(description='Apriori Algorithm.')
    argparser.add_argument(
        '-s', '--min_support',
        dest='min_support',
        help='minimum support',
        default=0.25,
        type=float
    )
    argparser.add_argument(
        '-c', '--min_confidence',
        dest='min_confidence',
        help='minimum confidence',
        default=0.5,
        type=float
    )
    argparser.add_argument(
        dest='filename',
        help='filename containing transactions',
        default='transactions.txt',
    )
    return argparser.parse_args()

def data_from_txt(filename):
    '''EXTRACTS DATABASE FROM .txt FILE'''
    file = open(filename, 'r')
    for line in file:
        row = line.strip().split()        
        yield row

def print_frequent_itemsets(itemset):
    '''PRINTS FREQUENT ITEMSETS'''
    print('========================')
    print('Itemset\t\tSupport')
    print('========================')
    for item in itemset.keys():
        print('%s\t\t%.3f' % (' '.join(sorted(list(item))), itemset[item]))

def print_association_rules(rules):
    '''PRINTS ASSOCIATION RULES'''
    print('========================================')
    print('    Rule\tConfidence\tSupport')
    print('========================================')
    rules.sort(key=lambda x: (len(x.A) + len(x.B), x.confidence, x.support, -x.time), reverse=True)
    for rule in rules:
        print(rule)

def main():
    '''MAIN METHOD'''
    min_support = 0.2
    min_confidence = 0.6
    data = data_from_txt('transactions.txt')    
    rules, itemset = Apriori(data, min_support, min_confidence).run()
    print('Mined {}\nand found a total of {} association rules:'.format('transactions', len(rules)))
    print_association_rules(rules)
    print_frequent_itemsets(itemset)

if __name__ == '__main__':
    main()
