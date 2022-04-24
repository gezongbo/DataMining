# -*- coding: utf-8 -*-
"""
Created on Sun Oct 17 19:08:42 2021

@author: sdeve
"""

from id3_c45 import DecisionTree
if __name__=='__main__':
	#Toy data
	X = [[1, 2, 0, 1, 0],
	[0, 1, 1, 0, 1],
	[1, 0, 0, 0, 1],
	[2, 1, 1, 0, 1],
	[1, 1, 0, 1, 1]]
	y = ['yes','yes','no','no','no']
		  
	clf = DecisionTree(mode='ID3')
	clf.fit(X,y)
	clf.show()
	print(clf.predict(X))   #['yes' 'yes' 'no' 'no' 'no']
		
	clf_ = DecisionTree(mode='C4.5')
	clf_.fit(X,y).show()
	print(clf_.predict(X))   #['yes' 'yes' 'no' 'no' 'no']