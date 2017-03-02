# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:Experiment.py
@time:2017/3/222:08
"""
import networkx as nx
from collections import defaultdict
import random

def selectQuery(G):
    '筛选查询节点和查询属性'
    '1. 实验的一些条件'
    qNumbers=[2,4,8,16,32] ##查询的节点数目
    cNumbers=[1,2,4,8,16,32] ##查询的coreness大小
    samples=30 ###
    samplePerCore=samples/cNumbers ##每个core执行的次数
    ###创建一个三维数组
    sampledNodes={}
    w=len(cNumbers)
    h=len(qNumbers)
    radius=samplePerCore
    for x in xrange(w):
        yhough = {}
        for y in xrange(h):
            rhough = {}
            for r in xrange(radius):
                rhough[r] = 0
            yhough[y] = rhough
        sampledNodes[x] = yhough

    '2. 从最大连通分量里面选'
    Gc=max(nx.connected_component_subgraphs(G),key=len)
    '3. 计算这个连通分量的k-core分解'
    coreIndex=nx.core_number(Gc)
    '4. 将节点按照core值分组'
     #将节点按照core number进行分组
    Vk=defaultdict(list) #字典的value是列表
    sortedVk={}
    for key in sorted(Vk.keys(),reverse=True):#Vk按照core值从大到小排序
        sortedVk[key]=Vk[key]
    '5. 按照core值和query数量生成查询节点集合'
    for i in range(len(cNumbers)):
        curCore=cNumbers[i] ##当前的core值
        '5.1:获取core>curCore的节点'
        coreNodes=[]
        for key in sortedVk.keys():
            if(key>=curCore):
                coreNodes.extend(sortedVk[key])
        '5.2:从候选节点里面获得最大连通分量'
        subGraph=Gc.subgraph(coreNodes)
        giantCC=max(nx.connected_component_subgraphs(subGraph),key=len)
        N=nx.number_of_nodes(giantCC)
        for j in range(len(qNumbers)):
            qn=qNumbers[j] ##查询节点数目
            if nx.number_of_nodes(giantCC)>=qn:
                for s in samplePerCore:
                    sample=randomSelectNode(giantCC,qn)
                    sampledNodes[i][j][s]=str(sample)
    '6. 输出查询节点'
    for j in range(len())


def randomSelectNode(giantCC,qn):
    res=set()
    nodeList=giantCC.nodes()
    N=nx.number_of_nodes(giantCC)
    while(len(res)<qn):
        rnd=random.randint(0,N)
        x=nodeList[rnd]
        res.add(x)
    return x







def getCoreNodes():
    '获取core>c的'