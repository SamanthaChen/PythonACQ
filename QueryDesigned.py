# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:QueryDesigned.py
@time:2017/3/222:08
@Function:根据文件，生成相应的查询文件
"""
import networkx as nx
from collections import defaultdict
import random

def selectQueryLimitedW(G,dataName,outputFile):
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
                attr=selectFrequentAttrs(giantCC,sample) ###选择几个出现频率最高的属性
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

def selectQueryAllW(G,dataName,outputFile):
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
                attr=selectAllAttrs(giantCC,sample) ###选择几个出现频率最高的属性
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

def selectFrequentAttrs(giantCC,sample):
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
        if count>=12:   #####这里设置选几个属性
            break
        res.append(tuple[0])
        count+=1
    return res

def selectAllAttrs(giantCC,sample):
    '选择所有查询节点的属性合集'
    allSet=set()
    for node in sample:
        if giantCC.node[node].has_key('attr'):
            for attr in giantCC.node[node]['attr']:
                allSet.add(attr)
    return list(allSet)

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
    G=nx.read_adjlist(adjlistFile,nodetype=int)
    ###读取属性文件，一行是一个节点和所有的属性
    f=open(attrFile)
    for line in f.readlines():
        words=line.split()
        id=int(words[0])
        attrs=words[1:]
        if G.has_node(id):##还得先判断有没有这个节点
            G.node[id]['attr']=attrs
    return G


def RunRandomSelectQuery():
    dataName='citeseer'
    edgefile='L:/ACQData/inputfile/'+dataName+'_graph'
    labelfile='L:/ACQData/inputfile/'+dataName+'_nodelabel'
    outputFile='L:/ACQData/'+dataName+'_Query_wall.txt';
    G=dataReader(edgefile,labelfile)
    print 'readed graph...'

    selectQueryAllW(G,dataName,outputFile)

def selectFromGroudTruthData():
    '从groud-truth data里面筛选查询节点，和查询属性'
    path='L:/ACQData/groundTruthData/'
    data='citeseer'
    dataName=data+'/'+data
    # edgeFile=open(path+dataName+' _graph','r')
    classFile=open(path+dataName+'_class','r')
    labelFile=open(path+dataName+'_nodelabel','r')
    queryFile=open(path+dataName+'_query_w2','w')
    wordNum=2 ###指定的筛选属性的个数

    '读社团分组'
    communityGroup = defaultdict(list)  ##社团分组
    for line in classFile.readlines():
        line=line.strip()
        words=line.split()
        communityGroup[words[1]].append(int(words[0]))
    classFile.close()
    '读节点标签'
    labelDict={}
    for line in labelFile.readlines():
        line=line.strip()
        words=line.split()
        labelDict[int(words[0])]=words[1:] ##属性还是str格式
    labelFile.close()
    '统计社团中属性出现频率'
    comWordFrequents={}
    comWordFrequents=comWordFrequents.fromkeys(communityGroup.keys(),{})##初始化
    comWordNodeGroup={}
    comWordNodeGroup=comWordNodeGroup.fromkeys(communityGroup.keys(),{})

    for className,nodes in communityGroup.items():
        wordFre={}
        wordNode=defaultdict(list)
        ###对于每个社团，统计一下词频
        for node in nodes:
            for label in labelDict[node]:
                if wordFre.has_key(label):
                    wordFre[label]+=1
                else:
                    wordFre[label]=1
                wordNode[label].append(node)
        ####
        comWordFrequents[className]=wordFre
        comWordNodeGroup[className]=wordNode


    '在同一个社团中,出现频率最大的k个关键词的查询组，随机选择[1,2,4,8,16]个查询节点'
    for className,wordNodeGroup in comWordNodeGroup.items():
        attrFreDict=comWordFrequents[className]
        attrNodeDict=comWordNodeGroup[className]
        '选择前两个属性'
        selectAttrs=[]
        tmp=sorted(attrFreDict.items(),key=lambda d:d[1],reverse=True)[0:wordNum] ##选择前wordNum个
        for tuple in tmp:
            selectAttrs.append(tuple[0]) ##只选择属性
        '在包含这些属性的节点里面选节点'
        nodeSet=set()
        for label in selectAttrs:
            for node in attrNodeDict[label]:
                nodeSet.add(node)
        '随机选节点'
        nodeList=list(nodeSet)
        countList=[1,2,4,8,16]
        for count in countList:
            selectNodeSet = set()
            while len(selectNodeSet)<count and len(nodeList)>=count:
                randIndex=random.randint(0,len(nodeList)-1)
                selectNodeSet.add(nodeList[randIndex])
            '选好节点，输出文件'
            string='qn:'+'\t'+str(count)+'\tnode:'
            for n in selectNodeSet:
                string+='\t'+str(n)
            string+='\t'+'attr:'
            for a in selectAttrs:
                string+='\t'+a
            queryFile.write(string+'\n')


if __name__=="__main__":
    selectFromGroudTruthData()