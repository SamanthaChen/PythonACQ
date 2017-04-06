# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:OnlineProcessingV3.py
@time:2017/3/2117:15
@Fuction：主要是为了实现GreedyInc

"""

import sys
sys.setrecursionlimit(1000000) #这里设置地柜深度为一百万
import networkx as nx
import copy
from math import log
from ShellStructIndex import ShellStructIndex as ShellIndex
from collections import defaultdict
import matplotlib.pyplot as plt
import Queue
from SteinTree import *
from LIHeuristic import LIHeuristic
from collections import deque
from OnlineProcessingV2 import *  ####这里是为了RetrieveCSM
from RankNode import RankNode



def greedyIncV2(G,H,requireK,queryVertexs,queryAttrs,alpha):
    '贪婪扩张子图'
    '在H（CSM或者CST）的结果中找斯坦纳树'
    stG = buildSteinerTree(queryVertexs, H)
    solution = stG.nodes()  ##当前解
    print 'stG is Connected?:',nx.is_connected(stG)
    '候选节点的当前度'
    candNodeDegree={}
    '候选节点的当前属性'
    '初始化查询属性列表'
    VwList={}
    VwList=VwList.fromkeys(queryAttrs,0) ##初始化
    for qa in queryAttrs:
        for n in solution:
            if G.node[n].has_key('attr') and G.node[n]['attr']!=None:
                if  qa in G.node[n]['attr']:
                    VwList[qa]+=1
    '存储最小度'
    graphMinDegree=[]
    minD=min(stG.degree().items(),key=lambda x:x[1])[1]
    graphMinDegree.append(minD) ##取最小度
    queue=[]
    while (not queue) or minD==requireK:
        '将当前结果集的邻居加入队列'








if __name__=="__main__":

    print 'ok'
