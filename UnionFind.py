# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:UnionFind.py
@time:2017/2/2020:42
"""
class UnionFind:
    '包含所有并查集方法的类'
    def makeSet(self,x): #这个x必须是UNode结构吗
        x.parent=x
        x.rank=0
        x.represent=x.value

    def find(self,x):
        if(x.parent!=x):
             x.parent=self.find(x.parent)
        return x.parent

    def union(self,x,y):
        xRoot=self.find(x)
        yRoot=self.find(y)
        if(xRoot==yRoot): return

        if(xRoot.rank<yRoot.rank):
            xRoot.parent=yRoot
        elif(xRoot.rank>yRoot.rank):
            yRoot.parent=xRoot
        else:
            yRoot.parent=xRoot
            xRoot.rank=xRoot.rank+1