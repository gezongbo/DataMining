# Examples of using the k-means and SOM algorithms on the Iris dataset

# import pylab as pl
import numpy as np
import kmeans

iris = np.loadtxt('data/iris_proc.data', delimiter=',') #载入数据
iris[:, :4] = iris[:, :4]-iris[:, :4].mean(axis=0) #每个属性值减去均值
imax = iris.max(axis=0) #每个属性（列）的最大值
iris[:, :4] = iris[:, :4]/imax[:4] #每个属性值除以最大值

target = iris[:,4] #分类标号列

#打乱数据的顺序
order = list(range(np.shape(iris)[0]))
np.random.shuffle(order)
iris = iris[order,:]
target = target[order]

train = iris[::2,0:4] #隔1行取1个数据，构成训练集
traint = target[::2]
valid = iris[1::4,0:4]#第1次取第1行，然后每隔3行取1个数据，构造验证集
validt = target[1::4]
test = iris[3::4,0:4] #第一次取第3行，然后每隔3行取1个数据，构造测试集
testt = target[3::4]

# print(train.max(axis=0), train.min(axis=0)) #打印训练数据每个属性的最大值和最小值


km = kmeans.kmeans(3,train)
km.kmeanstrain(train) #使用训练数据进行聚类
cluster = km.kmeansfwd(test) #使用最后获取的质心集判断测试数据分别属于那个类（与哪个质心最近）
print(cluster)
group = []
for element in cluster:
    group.append(element[0])
print(group) #输出聚类模型的预测结果
print(iris[3::4,4]) #输出原数据中的分类标号进行比较

