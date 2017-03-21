# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:DatasetAnalysis.py
@time:2017/3/1611:37
"""
import networkx as nx
from collections import defaultdict

def dataReader(graphFile,nodeFile):
    '根据图文件（邻接链表格式）和节点文件（节点-别名-属性）读取图'
    G=nx.read_adjlist(graphFile,nodetype=int) #从邻接表读取图数据
    #读取节点的属性文件
    f=open(nodeFile)
    for line in f.readlines():
        line=line.strip('\n')
        words = line.split('\t') ###name和属性是ab分割，但是属性是空格分割
        attrs=words[2].split(' ')
        G.node[int(words[0])]["name"]=words[1] #读取节点的name
        G.node[int(words[0])]["attr"]=attrs #读取节点的属性
    return G

def dataReader3(adjlistFile,attrFile):
    '读取（节点，节点邻接链表），（节点，属性列表）的文件'
    G=nx.read_adjlist(adjlistFile,nodetype=int)
    ###################处理一下有节点没有属性的情况（2017.3.4）
    for n in G.nodes():
        G.node[n]['attr']=None
    ###读取属性文件，一行是一个节点和所有的属性
    f=open(attrFile)
    for line in f.readlines():
        line=line.strip('\n')
        words=line.split()
        id=int(words[0])
        attrs=words[1:]
        if G.has_node(id):###可能存没有节点但是有属性
            G.node[id]['attr']=attrs
    return G

if __name__=='__main__':
    path = 'L:/ACQData/'
    dataset = 'dblp'

    'facebook'
    # ego='3980'
    # edgefile = path + 'groundTruthData/' + dataset + '/' + dataset + '_ego'+ego+'_graph'
    # labelfile = path + 'groundTruthData/' + dataset + '/' + dataset + '_ego'+ego+'_nodelabel'
    # classFile = path + 'groundTruthData/' +dataset + '/' + dataset + '_ego'+ego+'_class'

    'groundTruthData'
    # edgefile = path + 'groundTruthData/' + dataset + '/' + dataset +'_graph'
    # labelfile = path + 'groundTruthData/' + dataset + '/' + dataset +'_nodelabel'
    # classFile = path + 'groundTruthData/' +dataset + '/' + dataset +'_class'

    'no groundTruth'
    edgefile = path + 'inputfile/'  + dataset +'_graph'
    labelfile = path + 'inputfile/' + dataset +'_nodelabel'


    print 'Reading graph...'
    G = dataReader3(edgefile, labelfile)
    print 'nodes number:',len(G)
    print 'edges number:',len(G.edges())


    '节点度分布'
    degreeDict=nx.degree(G)
    maxDegree=max(degreeDict.items(),key=lambda x:x[1])[1]
    print 'max degree:',maxDegree
    coreDict=nx.core_number(G)
    maxCoreness=max(coreDict.items(),key=lambda d:d[1])[1]
    print 'max coreness:',maxCoreness

    '读节点标签'
    labelDict = {}
    labelGroup=defaultdict(list)
    lf=open(labelfile,'r')
    for line in lf.readlines():
        line = line.strip()
        words = line.split()
        labelDict[int(words[0])] = words[1:]  ##属性还是str格式
        for a in words[1:]:
            labelGroup[a].append(int(words[0]))
    lf.close()
    print 'label number:',len(labelGroup.keys())

    '读社团分组'
    # communityGroup = defaultdict(list)  ##社团分组
    # nodeClassDict = {}
    # cf=open(classFile,'r')
    # for line in cf.readlines():
    #     line = line.strip()
    #     words = line.split()
    #     nodeClassDict[int(words[0])] = words[1]
    #     communityGroup[words[1]].append(int(words[0]))
    # cf.close()
    # print 'class number:',len(communityGroup.keys())
