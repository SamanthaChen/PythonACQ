# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:UNode.py
@time:2017/2/2020:36
"""
class UNode:
    '并查集的数据结构'
    def __init__(self,value):
        self.value=value
        self.parent=None #假设默认是-1
        self.rank=-1
        self.represent=-1

    # def __str__(self):
    #     return 'value:'+str(self.value)+' rank:'+str(self.rank)+' parent:'+str(self.parent)