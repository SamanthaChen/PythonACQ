# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:TNode.py
@time:2017/2/2016:54
"""
class TNode:
    '索引树的class'
    def __init__(self,core=0,data='root'):
        self.core = core
        self.nodeList=[]
        self.childList=[]
        self.kwMap=[]
        self.data=data
        self.parent=self

    def __str__(self):
        return 'core:'+str(self.core)+',nodeList:'+str(self.nodeList)


