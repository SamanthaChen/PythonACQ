# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:QueryDesigedTime.py
@time:2017/4/1215:32
生成关于时间的查询文件
"""
import networkx as nx
from collections import defaultdict
import random

def selectQueryLimitedW(G,dataName,outputFile,cNumbers,attrNumberList):
    '筛选查询节点和查询属性'
    '1. 实验的一些条件'
    qNumbers=[1,2,4,8,16,32] ##查询的节点数目[2,4,8,16,32]
    # cNumbers=[1,2,4,8,16,32] ##查询的coreness大小
    samples=30 ###
    # samplePerCore=samples/len(cNumbers) ##每个core执行的次数
    ###创建一个二维数组
    sampledNodes=[['' for j in range(len(qNumbers))] for i in range(len(cNumbers))]
    attrs=[['' for j in range(len(qNumbers))] for i in range(len(cNumbers))] ##属性
    '2. 从最大连通分量里面选'
    Gc=max(nx.connected_component_subgraphs(G),key=len)
    '3. 计算这个连通分量的k-core分解'
    coreIndex=nx.core_number(Gc)
    '4. 将节点按照core值分组'
     #将节点按照core number进行分组
    Vk=defaultdict(list)
    for key,value in coreIndex.items():
        Vk[value].append(key)
    # tmpVk=sorted(Vk.iteritems(), key=lambda d:d[0],reverse=False)#Vk按照core值从大到小排序
    mxCore=max(Vk.keys())  ##这个图的最大core
    '5. 按照core值和query数量生成查询节点集合'

    for i in range(len(cNumbers)):
        curCore=cNumbers[i] ##当前的core值
        '假设core还大于这个图最大core，重新设置一个core(随机生成)'
        if curCore>mxCore: ###当前的core达不到要求啊，就不往下找了
            curCore=random.randint(1,mxCore)
        '5.1:获取core>curCore的节点'
        coreNodes=[]
        for key in Vk.keys():
            if(key>=curCore):
                coreNodes.extend(Vk[key])

        '5.2:从候选节点里面获得最大连通分量'
        subGraph=Gc.subgraph(coreNodes)
        giantCC=max(nx.connected_component_subgraphs(subGraph),key=len)
        N=nx.number_of_nodes(giantCC)
        for j in range(len(qNumbers)):
            qn=qNumbers[j] ##查询节点数目
            '假设coreNodes个数还小于需要的查询节点数，重新设置一个Qn(随机生成)'
            if len(coreNodes) < qn:
                qn=random.randint(1,len(coreNodes))
            if nx.number_of_nodes(giantCC)>=qn:
                sample=randomSelectNode(giantCC,qn) ###随机选qn个节点
                s1='\t'.join([str(val) for val in sample])
                sampledNodes[i][j]=s1##列表变成string
                for attrNumber in attrNumberList:
                    attr=selectFrequentAttrs(giantCC,sample,attrNumber) ###选择几个出现频率最高的属性
                    attrs[i][j]='\t'.join([val for val in attr])


    '6. 输出查询节点'
    f=open(outputFile,'w')
    for i in range(len(cNumbers)):
        core=cNumbers[i]
        for j in range(len(qNumbers)):
            qn=qNumbers[j]
            string='core:\t'+str(core)+'\tqn:\t'+str(qn)+'\tnode:\t'+sampledNodes[i][j]+'\tattr:\t'+attrs[i][j]
            f.write(string+'\n')
    f.close()

def selectFrequentAttrs(giantCC,sample,attrNumber):
    '这里选的属性默认是6个'
    words={}
    res=[]
    for node in sample:
        for attr in giantCC.node[node]['attr']:
            if attr not in words:
                words[attr]=0
            words[attr]+=1
    ###选择6个出现频率最高的
    sortedWords= sorted(words.iteritems(), key=lambda d:d[1], reverse = True)
    count=0
    for tuple in sortedWords:
        if count>=attrNumber:   #####这里设置选几个属性
            break
        res.append(tuple[0])
        count+=1
    return res

def randomSelectNode(giantCC,qn):
    res=set() ###节点集合
    attrs=[]  ###属性集合
    nodeList=giantCC.nodes()
    N=nx.number_of_nodes(giantCC)
    while(len(res)<qn):
        rnd=random.randint(0,N-1)###注意这个随机数包括区间的两个范围
        x=nodeList[rnd]
        res.add(x)
    return res

def RunRandomSelectQueryFB():
    egoList=[0,107,348,414,686,698,1684,1912,3437,3980]
    egoList2=[1684]


    for dataName in egoList2:
        edgefile='L:/ACQData/groundTruthData/facebook/facebook_ego'+str(dataName)+'_graph'
        labelfile='L:/ACQData/groundTruthData/facebook/facebook_ego'+str(dataName)+'_nodelabel'
        outputFile = 'L:/ACQData/groundTruthData/facebook/facebook_ego' + str(dataName) + '_query_core_times'
        attrNumberList=[1,2,3,4,5,6,7,8,9,10]
        cNumbers = [1, 2, 4, 8, 12, 16, 18, 24, 28, 32]
        for attrNumber in attrNumberList:
            print 'readed graph facebook_ego',dataName,'......'
            selectQueryLimitedW(G,dataName,outputFile,cNumbers,attrNumber)