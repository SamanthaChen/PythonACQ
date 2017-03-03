# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:Experiment.py
@time:2017/3/222:08
@Function:根据文件，生成相应的查询文件
"""
import networkx as nx
from collections import defaultdict
import random

def selectQuery(G,dataName,outputFile):
    '筛选查询节点和查询属性'
    '1. 实验的一些条件'
    qNumbers=[2,4,8,16,32] ##查询的节点数目
    cNumbers=[1,2,4,8,16,32] ##查询的coreness大小
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
        if curCore>mxCore: ###当前的core达不到要求啊，就不往下找了
            break
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
            if nx.number_of_nodes(giantCC)>=qn:
                sample=randomSelectNode(giantCC,qn) ###随机选qn个节点
                s1='\t'.join([str(val) for val in sample])
                sampledNodes[i][j]=s1##列表变成string
                attr=frequentAttrs(giantCC,sample) ###选择几个出现频率最高的属性
                attrs[i][j]='\t'.join([val for val in attr])

    '6. 输出查询节点'
    f=open(outputFile,'w')
    for i in range(len(cNumbers)):
        core=cNumbers[i]
        for j in range(len(qNumbers)):
            qn=qNumbers[j]
            string='core:\t'+str(core)+'\tqn:\t'+str(qn)+'\tnode:\t'+sampledNodes[i][j]+'\tattrs:\t'+attrs[i][j]
            f.write(string+'\n')
    f.close()


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

def frequentAttrs(giantCC,sample):
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
        if count>=6:
            break
        res.append(tuple[0])
        count+=1
    return res

def dataReader2(edgefile,attrfile):
    '读的是delicious类型的数据'
    G=nx.read_edgelist(edgefile,nodetype=int) #从邻接表读取图数据
    #读取节点的属性文件(一行只有一个节点一个属性)
    f=open(attrfile)
    for line in f.readlines():
        words=line.split() ##第一个是id，后面跟着的都是属性
        id=int(words[0])
        attr=words[1]
        if G.has_node(id):
            if G.node[id].has_key('attr'):
                G.node[id]['attr'].append(attr)
            else:
                G.node[id]['attr']=[] #新加一个列表
    return G

def dataReader(adjlistFile,attrFile):
    G=nx.read_adjlist(edgefile,nodetype=int)
    ###读取属性文件，一行是一个节点和所有的属性
    f=open(attrFile)
    for line in f.readlines():
        words=line.split()
        id=int(words[0])
        attrs=words[1:]
        G.node[id]['attr']=attrs
    return G


if __name__=="__main__":
    dataName='delicious'
    edgefile='L:/ACQData/inputfile/'+dataName+'_graph'
    labelfile='L:/ACQData/inputfile/'+dataName+'_nodelabel'
    outputFile='L:/ACQData/'+dataName+'_Query.txt';
    G=dataReader(edgefile,labelfile)
    print 'readed graph...'

    selectQuery(G,dataName,outputFile)