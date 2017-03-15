# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:TNode.py
@time:2017/2/2016:54
@Revise:
"""

class TNode:
    '索引树的class'
    def __init__(self,core=0,data=0):
        self.core = core
        self.nodeList=[] #包含的图节点的ID
        self.childList=[] #包含的TNode孩子节点
        self.kwMap=[] #nodeList里面节点属性的倒排
        self.data=data #节点编号
        self.parent=self

    def __str__(self):
        return 'core:'+str(self.core)+',nodeList:'+str(self.nodeList)


