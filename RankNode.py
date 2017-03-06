# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:RankNode.py
@time:2017/3/521:34
"""
class RankNode:
    id=-1


    '''可排序的类'''
    def __init__(self,id,connection,attrScore):
        self.id=id
        self.connection=connection
        self.attrScore=attrScore

    def __cmp__(self, other):
        if self.id==other.id:
            return 0
        elif self.connection>other.connection:
            return -1
        elif self.connection<other.connection:
            return 1
        elif self.attrScore>other.attrScore:
            return -1
        elif self.attrScore<other.attrScore:
            return 1
        elif self.id>other.id:
            return 1
        elif self.id<other.id:
            return -1
        else:
            return 0


    def __str__(self):
        return 'id:'+str(self.id)+' con:'+str(self.connection)+' atts:'+str(self.attrScore)
