# K-means Algorithm by zhang Oct 30, 2019

import numpy as np

class kmeans:
	""" The k-Means algorithm"""
	def __init__(self,k,data):

		self.nData = np.shape(data)[0] #行的个数（有多少个数据）
		self.nDim = np.shape(data)[1] #列的个数（有多少个属性）
		self.k = k #要分为几类（聚类的簇数，cluster number）
		
	def kmeanstrain(self,data,maxIterations=10):
		
		# Find the minimum and maximum values for each feature
        # 找出每个属性的最大值和最小值
		minima = data.min(axis=0)
		maxima = data.max(axis=0)
	
		# Pick the centre locations randomly
        # 使用每个属性的最大值和最小值随机产生初始质心组（生成了两组，假设一组是当前的，一组是（不存在的）上一次的）
		self.centres = np.random.rand(self.k,self.nDim)*(maxima-minima)+minima
		oldCentres = np.random.rand(self.k,self.nDim)*(maxima-minima)+minima
	
		count = 0
		#print centres
		while np.sum(oldCentres-self.centres)!= 0 and count<maxIterations: #如果前一次的质心组和这次的质心组相比有变化
	
			oldCentres = self.centres.copy() #将当前质心组复制给前一次质心组
			count += 1
	
			# 计算每个数据与每个质心的距离，判断其属于哪个质心，完成后，不同的质心用属于自己的数据更新自身
            
            # 计算所有数据和所有质心的距离
			distances = np.ones((1,self.nData))*np.sum((data-self.centres[0,:])**2,axis=1)			
			for j in range(self.k-1):
				distances = np.append(distances,np.ones((1,self.nData))*np.sum((data-self.centres[j+1,:])**2,axis=1),axis=0)
	
			# Identify the closest cluster
			cluster = distances.argmin(axis=0) #找出每个数据所属的质心（簇) 			
			cluster = np.transpose(cluster*np.ones((1,self.nData))) #转换成列向量的形式（只有一列的矩阵）           
	
			# Update the cluster centres
            # 更新每个质心
			for j in range(self.k):
				thisCluster = np.where(cluster==j,1,0) #筛选属于当前质心数据的逻辑向量（若该数据属于当前质心，相应位置为1，否则为0）				
				if sum(thisCluster)>0:
					self.centres[j,:] = np.sum(data*thisCluster,axis=0)/np.sum(thisCluster) #更新质心
                    
		print(self.centres) #输出最后质心组
                
		return self.centres
	
	def kmeansfwd(self,data):
		
		nData = np.shape(data)[0] #数据个数
		# Compute distances
        # 计算每个数据与每个质心的距离
		distances = np.ones((1,nData))*np.sum((data-self.centres[0,:])**2,axis=1)
		for j in range(self.k-1):
			distances = np.append(distances,np.ones((1,nData))*np.sum((data-self.centres[j+1,:])**2,axis=1),axis=0)	
		
		# Identify the closest cluster
		cluster = distances.argmin(axis=0) #确定每个数据属于哪个质心（簇）		 
		cluster = np.transpose(cluster*np.ones((1,nData))) # 转换为列向量（只有一列的矩阵）		        
		return cluster
