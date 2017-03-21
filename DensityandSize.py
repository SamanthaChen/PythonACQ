# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:DensityandSize.py
@time:2017/3/179:49
"""
import networkx as nx

def computeDensityLDense(data):
    '计算Ldense结果的密度'
    # data='citeseer'
    algo='LDense'
    graphFile='L:/ACQData/groundTruthData/'+data+'/'+data+'_graph'
    # resFile='L:/ACQData/'+algo+'/'+data+'_query_w2_csmGrd_res.txt'
    resFile = 'L:/ACQData/' + algo + '/' + data +'/'+data+ '_100' ###Lense的结果文件
    queryFile='L:/ACQData/groundTruthData/'+data+'/'+data+'_query_2Nei_w3_100'
    labelFile='L:/ACQData/groundTruthData/'+data+'/'+data+'_nodelabel'
    '0:读图'
    G=nx.read_adjlist(graphFile,nodetype=int)
    '1:把社团读进来'
    communityList = []
    resf = open(resFile, 'r')
    for line in resf.readlines():
        line = line.strip()
        words = line.split()
        com = [int(val) for val in words]
        communityList.append(com)
    resf.close()
    '2:读查询节点，查询属性。'
    queryAttrs = []
    queryNodes = []
    qaf = open(queryFile, 'r')
    for line in qaf.readlines():
        line = line.strip()
        words = line.split()
        nodeStartid = words.index('node:')
        attrsStartid = words.index('attr:')  ####查询属性开始的位置
        attrList = words[attrsStartid + 1:]
        nodeList = [int(val) for val in words[nodeStartid + 1:attrsStartid]]
        queryAttrs.append(attrList)
        queryNodes.append(nodeList)
    qaf.close()
    '3.读取节点的标签'
    nodeAttrDict = {}
    lq = open(labelFile, 'r')
    for line in lq.readlines():
        line = line.strip()
        words = line.split()
        nodeAttrDict[int(words[0])] = words[1:]
    lq.close()
    '4:确定涉及查询节点的社团'
    relatedComs = []
    for j in range(len(queryNodes)):
        nodeList = queryNodes[j]
        comSet = set()
        for n in nodeList:
            for i in range(len(communityList)):
                if n in communityList[i]:
                    comSet.add(i)
        relatedComs.append(list(comSet))
    '5:计算size和密度'
    sizeListAverList=[]
    densityListAverList=[]
    linecount=0
    for comidList in relatedComs:
        densityList=[]
        sizeList=[]
        # print 'line 1:',linecount
        linecount+=1
        for comid in comidList:
            com=communityList[comid]
            sizeList.append(len(com))
            subgraph=G.subgraph(com)
            tmpden=nx.density(subgraph)
            densityList.append(tmpden)
        # print 'sizeList:',sizeList
        # print 'densityList:',densityList
        aversize=0
        averden=0
        if len(densityList)>0:
            averden=float(sum(densityList))/float(len(densityList))
        if len(sizeList)>0:
            aversize=float(sum(sizeList))/float(len(sizeList))
        sizeListAverList.append(aversize)
        densityListAverList.append(averden)
    allsizeaver=0
    alldensaver=0
    print 'all size:',sizeListAverList
    if len(sizeListAverList)>0:
        allsizeaver=float(sum(sizeListAverList))/float(len(sizeListAverList))
    print 'all size aver:',allsizeaver
    print  'all density:',densityListAverList
    if len(densityListAverList)>0:
        alldensaver=float(sum(densityListAverList))/float(len(densityListAverList))
    print 'all dens aver:',alldensaver

def computeDensity(data):
    '计算一般结果的密度'
    # data='citeseer'
    algo='greedyInc'
    graphFile='L:/ACQData/groundTruthData/'+data+'/'+data+'_graph'
    resFile='L:/ACQData/'+algo+'/'+data+'_query_2Nei_w3_100_onlyNode_cocktail_res.txt' ###cocktailparty的
    resFile = 'L:/ACQData/' + algo + '/' + data + '_query_2Nei_w3_100_csm_res_a10.txt'
    queryFile = 'L:/ACQData/groundTruthData/' + data + '/' + data + '_query_2Nei_w3_100'
    labelFile='L:/ACQData/groundTruthData/'+data+'/'+data+'_nodelabel'
    '0:读图'
    G=nx.read_adjlist(graphFile,nodetype=int)
    '1:把社团读进来'
    communityList = []
    resf = open(resFile, 'r')
    for line in resf.readlines():
        line = line.strip()
        words = line.split()
        com = [int(val) for val in words]
        communityList.append(com)
    resf.close()
    '2:读查询节点，查询属性。'
    queryAttrs = []
    queryNodes = []
    qaf = open(queryFile, 'r')
    for line in qaf.readlines():
        line = line.strip()
        words = line.split()
        nodeStartid = words.index('node:')
        attrsStartid = words.index('attr:')  ####查询属性开始的位置
        attrList = words[attrsStartid + 1:]
        nodeList = [int(val) for val in words[nodeStartid + 1:attrsStartid]]
        queryAttrs.append(attrList)
        queryNodes.append(nodeList)
    qaf.close()
    '3.读取节点的标签'
    nodeAttrDict = {}
    lq = open(labelFile, 'r')
    for line in lq.readlines():
        line = line.strip()
        words = line.split()
        nodeAttrDict[int(words[0])] = words[1:]
    lq.close()

    '5:计算size和密度'
    sizeList=[]
    densityList=[]
    minDList=[]
    linecount=0
    for com in communityList:
        sizeList.append(len(com))
        subgraph=G.subgraph(com)
        densityList.append(nx.density(subgraph))
        '计算最小度'
        degrees=nx.degree(subgraph)
        minD=min(degrees.items(),key=lambda d:d[1])[1]
        minDList.append(minD)
    sizeaver=0
    denaver=0
    print 'all size:',sizeList
    if len(sizeList)>0:
        sizeaver=float(sum(sizeList))/float(len(sizeList))
    print 'size aver:',sizeaver
    print 'all dens:',densityList
    if len(densityList)>0:
        denaver=float(sum(densityList))/float(len(densityList))
    print  'dens aver:',denaver
    '最小度打印'
    print 'all mind:',minDList



if __name__=='__main__':
    # dataList=['citeseer','cora','cornell','texas','wisconsin','washington']
    # for data in dataList:
    #     print '*********************************'
    #     print 'data=',data
    #     computeDensity(data)
    # computeDensityLDense('citeseer')

    computeDensity('citeseer')