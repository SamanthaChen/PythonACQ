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

def selectQueryLimitedW(G,dataName,outputFile,cNumbers,attrNumber):
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
            string='core:\t'+str(core)+'\tqn:\t'+str(qn)+'\tnode:\t'+sampledNodes[i][j]+'\tattr:\t'+attrs[i][j]
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
    dataList=['citeseer','cora','cornell','texas','wisconsin','washington']
    dataList2=['imdb']
    for dataName in dataList2:
        edgefile='L:/ACQData/inputfile/'+dataName+'_graph'
        labelfile='L:/ACQData/inputfile/'+dataName+'_nodelabel'
        attrNumber = 3
        outputFile='L:/ACQData/inputfile/'+dataName+'/'+dataName+'_query_core_w'+str(attrNumber)+'_5'
        cNumbers = [1, 2, 4, 8, 16, 32]  ##查询的coreness大小
        G=dataReader(edgefile,labelfile)
        print 'readed graph',dataName,'......'
        selectQueryLimitedW(G,dataName,outputFile,cNumbers,attrNumber)

def RunRandomSelectQueryFB():
    egoList=[0,107,348,414,686,698,1684,1912,3437,3980]

    for dataName in egoList:
        edgefile='L:/ACQData/groundTruthData/facebook/facebook_ego'+str(dataName)+'_graph'
        labelfile='L:/ACQData/groundTruthData/facebook/facebook_ego'+str(dataName)+'_nodelabel'
        attrNumber = 3
        outputFile='L:/ACQData/groundTruthData/facebook/facebook_ego'+str(dataName)+'_query_core3_w'+str(attrNumber)+'_10'
        cNumbers=[1,2,4,8,12,16,18,24,28,32]
        G=dataReader(edgefile,labelfile)
        print 'readed graph facebook_ego',dataName,'......'
        selectQueryLimitedW(G,dataName,outputFile,cNumbers,attrNumber)

def selectFromGroudTruthData():
    '从groud-truth data里面筛选查询节点，和查询属性'
    path='L:/ACQData/groundTruthData/'
    data='citeseer'
    dataName=data+'/'+data
    # edgeFile=open(path+dataName+' _graph','r')
    classFile=open(path+dataName+'_class','r')
    labelFile=open(path+dataName+'_nodelabel','r')
    queryFile=open(path+dataName+'_query_w2_1','w')
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


def analyzeGroundTruthData():
    '分析一下数据'
    '从groud-truth data里面筛选查询节点，和查询属性'
    path = 'L:/ACQData/groundTruthData/'
    data = 'citeseer'
    dataName = data + '/' + data
    # edgeFile=open(path+dataName+' _graph','r')
    classFile = open(path + dataName + '_class', 'r')
    labelFile = open(path + dataName + '_nodelabel', 'r')
    analyzedFile = open(path + dataName + '_analyzeKeyWord', 'w')
    wordNum = 10  ###指定的筛选属性的个数

    '读社团分组'
    communityGroup = defaultdict(list)  ##社团分组
    for line in classFile.readlines():
        line = line.strip()
        words = line.split()
        communityGroup[words[1]].append(int(words[0]))
    classFile.close()
    '读节点标签'
    labelDict = {}
    for line in labelFile.readlines():
        line = line.strip()
        words = line.split()
        labelDict[int(words[0])] = words[1:]  ##属性还是str格式
    labelFile.close()
    '统计社团中属性出现频率'
    comWordFrequents = {} ##{社团：{关键词：频率}}
    comWordFrequents = comWordFrequents.fromkeys(communityGroup.keys(), {})  ##初始化
    comWordNodeGroup = {} ##{社团：{关键词：包含的社团中的节点集}}
    comWordNodeGroup = comWordNodeGroup.fromkeys(communityGroup.keys(), {})

    for className, nodes in communityGroup.items():
        wordFre = {}
        wordNode = defaultdict(list)
        ###对于每个社团，统计一下词频
        for node in nodes:
            for label in labelDict[node]:
                if wordFre.has_key(label):
                    wordFre[label] += 1
                else:
                    wordFre[label] = 1
                wordNode[label].append(node)
        ####
        comWordFrequents[className] = wordFre
        comWordNodeGroup[className] = wordNode

    '输出文件'
    for className in comWordFrequents.keys():
        attrFreDict = comWordFrequents[className]
        attrNodeDict = comWordNodeGroup[className]
        '选择前wordnum个属性'
        selectAttrs = []
        tmp = sorted(attrFreDict.items(), key=lambda d: d[1], reverse=True)[0:wordNum]  ##选择前wordNum个
        for tuple in tmp:
            selectAttrs.append(tuple[0])  ##只选择属性
        '输出分析结果'
        outstr='class: '+className+'\n'
        printStr='class: '+className+'\tkeywords:'
        for a in selectAttrs:
            outstr+='keyword: '+str(a)+'\tFrequent: '+str(attrFreDict[a])+'\tNodes: '
            printStr+=str(a)+' '
        print printStr
            # for n in attrNodeDict[a]:
            #     outstr+=str(n)+', '
            # outstr+='\n'
        # analyzedFile.write(outstr+'\n')
    # analyzedFile.close()


def selectFromGroudTruthDataFrom2Nei(data,queryTimes,wordNum):
    '从groud-truth data里面筛选查询节点，和查询属性'
    path='L:/ACQData/groundTruthData/'
    # data='washington'
    dataName=data+'/'+data
    edgePath=path+dataName+'_graph'
    classFile=open(path+dataName+'_class','r')
    labelFile=open(path+dataName+'_nodelabel','r')
    # queryTimes = 10
    queryFile=open(path+dataName+'_query_2Nei_w3_'+str(queryTimes),'w')

    # wordNum=3 ###指定的筛选属性的个数

    '读图'
    G=nx.read_adjlist(edgePath,nodetype=int)
    ##获取度
    degreeDict=nx.degree(G)
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
        attrNodeDict=comWordNodeGroup[className] ###这个社团里面的
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
        '选择社团里面度最大的节点以及他的邻居'
        maxDNode=nodeSet.pop()
        maxD=degreeDict[maxDNode]
        for node in nodeSet:
            if degreeDict[node]>maxD:
                maxDNode=node
                maxD=degreeDict[node]
        '随机选度最大的节点的邻居,一个社团生成十次查询文件'
        for i in range(queryTimes):
            count=random.randint(1,maxD-1)
            '在度最大的节点的2度邻居里面选'
            oneHopNeis=nx.neighbors(G,maxDNode)
            twoHopneis=[]
            for n in oneHopNeis:
                twoHopneis.extend(nx.neighbors(G,n))     ##2度邻居
            '节点筛选范围是nodeList'
            nodeList=[]
            nodeList.extend(oneHopNeis)
            nodeList.extend(twoHopneis)
            selectNodeSet = set()  ##最终入选的节点集
            while len(selectNodeSet) < count and len(nodeList) >= count:
                randIndex = random.randint(0, len(nodeList) - 1)
                selectNodeSet.add(nodeList[randIndex])
            '选好节点，输出文件'
            string = 'qn:' + '\t' + str(count) + '\tnode:'
            for n in selectNodeSet:
                string += '\t' + str(n)
            string += '\t' + 'attr:'
            for a in selectAttrs:
                string += '\t' + a
            queryFile.write(string + '\n')



if __name__=="__main__":
    # selectFromGroudTruthData()
    # RunRandomSelectQuery()
    # analyzeGroundTruthData()
    # dataList=['texas','cornell','wisconsin','washington','cora','citeseer']
    # for data in dataList:
    #     selectFromGroudTruthDataFrom2Nei(data,10,3)

    RunRandomSelectQuery()
    # RunRandomSelectQueryFB()
