# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:OnlineProcessingV2.py
@time:2017/3/1020:42
@Function：在先查询方法的类（新修订版）
"""
import sys
sys.setrecursionlimit(1000000) #例如这里设置为一百万
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

def retrieveCSMV2(queryVertexes,index):
    '获得查询节点的最低公共祖先的coreness大小'
    '预处理'
    vertexTNodeList = index.vertexTNodelist  ##先把图节点到树节点的映射拿出来
    coreDict=index.coreDict
    '1:获得查询节点中最大的coreness'
    tmpSet=set()
    for qv in queryVertexes:
        tmpSet.add(coreDict[qv])
    maxQCore=max(tmpSet)
    k=maxQCore
    '2:从最底下一层开始'
    querys=copy.deepcopy(queryVertexes)  # 复制一个新的，因为后面要删除
    candiatelca=set()
    for qv in queryVertexes:
        if(index.coreDict[qv]==k):
            candiatelca.add(vertexTNodeList[qv]) ###存查询节点属于的树节点
            querys.remove(qv)
    '3:从k-1层开始慢慢往上找'
    while (len(querys)!=0   or  len(candiatelca)!=1):
        ctmp=set()
        for tnode in candiatelca:##将k层候选节点的父母加进来(core大于等于k-1的树节点)
            ctmp.add(tnode.parent)
        for qv in queryVertexes:
            if coreDict[qv]==k-1: ##将k-1层的包含查询节点的树节点加进来
                ctmp.add(vertexTNodeList[qv])
                querys.remove(qv)
        candiatelca=copy.deepcopy(ctmp)
        k=k-1
    ###最低公共祖先应该是最后一个core等于k的
    lcaroot=candiatelca.pop()
    for tnode in candiatelca:
        if tnode.core==k:
            lcaroot=tnode
    '5:找到最低lca后，BFS遍历树，返回所包含的所有图节点'
    queue=deque()
    queue.append(lcaroot)
    resvertexes=[]
    while queue:
        tnode=queue.pop()
        resvertexes.extend(tnode.nodeList)
        if tnode.childList:
            queue.extend(tnode.childList)
    print resvertexes
    '6:返回包含的子图'
    H=index.G.subgraph(resvertexes)
    return resvertexes,H,k

def retrieveCSTV2(queryVertexes,index,requireK):
    '先找最低公共祖先，再往上找到最小k'
    '预处理'
    vertexTNodeList = index.vertexTNodelist  ##先把图节点到树节点的映射拿出来
    coreDict = index.coreDict
    '1:获得查询节点中最大的coreness'
    tmpSet = set()
    for qv in queryVertexes:
        tmpSet.add(coreDict[qv])
    maxQCore = max(tmpSet)
    k = maxQCore
    '查询节点最大的coreness都没有要求的大，直接返回'
    if maxQCore<requireK:
        return None,None,None
    '2:从最底下一层开始'
    querys = copy.deepcopy(queryVertexes)  # 复制一个新的，因为后面要删除
    candiatelca = set()
    for qv in queryVertexes:
        if (index.coreDict[qv] == k):
            candiatelca.add(vertexTNodeList[qv])  ###存查询节点属于的树节点
            querys.remove(qv)
    '3:从k-1层开始慢慢往上找'
    while (len(querys) != 0 or len(candiatelca) != 1) and k>=0:
        ctmp = set()
        for tnode in candiatelca:  ##将k层候选节点的父母加进来(core大于等于k-1的树节点)
            ctmp.add(tnode.parent)
        for qv in queryVertexes:
            if coreDict[qv] == k - 1:  ##将k-1层的包含查询节点的树节点加进来
                ctmp.add(vertexTNodeList[qv])
                querys.remove(qv)
        candiatelca = copy.deepcopy(ctmp)
        k = k - 1
    ###最低公共祖先应该是最后一个core等于k的
    lcaroot = candiatelca.pop()
    for tnode in candiatelca:
        if tnode.core == k:
            lcaroot = tnode
    '5:找到最低lca后，先判断是否符合要求'
    cstlca=lcaroot
    if k<requireK:
        print 'No cst...Return csm...'
        return None,None,None
    else:
        '找到cst的lca'
        tmpk=k
        while tmpk>requireK and cstlca.parent:
            cstlca=cstlca.parent
            tmpk=cstlca.core
    '6:从最低祖先开始遍历树，找到符合条件的子图'
    queue = deque()
    queue.append(cstlca)
    resvertexes = []
    while queue:
        tnode = queue.pop()
        resvertexes.extend(tnode.nodeList)
        if tnode.childList:
            queue.extend(tnode.childList)
    print resvertexes
    '6:返回包含的子图'
    H = index.G.subgraph(resvertexes)
    return resvertexes, H, k

def greedyDecV2(H,requireK,queryVertexes,queryAttributes):
    '从候选图H，以及规定的k中迭代删除最小得分的节点。这里还考虑到删除节点会对邻居构成的影响'
    '1：先获取初始的候选子图'
    Hi=copy.deepcopy(H) #深拷贝一个子图
    deletedVertexes=[] ##删除的节点
    graphAttrScores={} ##存删除每个节点后对应的子图得分(re:2017.3.12：改成字典)
    '2: 计算每个查询属性覆盖的节点个数'
    VwList=computeVwList(queryAttributes,Hi)
    print 'VwList:', VwList, '\tlen(Hi):', str(len(Hi))
    '3: 计算初始的图的属性得分'
    score0=sum([float(val*val)/float(len(Hi)) for val in VwList.values()]) ###sum(Vw*Vw/|V(H)|)
    graphAttrScores[0]=score0
    '4: 计算除了查询节点外，每个节点的属性分和边缘属性得分'
    vertexAttrMarginalGain=computeVertexAttrScore(H,VwList,queryAttributes,queryVertexes,requireK)
    '5: 循环删除节点'
    deletedCount=0
    while isConnectedinG(queryVertexes,Hi):
        '5.1: 删除边缘属性得分最小的节点'
        if not vertexAttrMarginalGain: ##假如已经遍历完所有的候选节点
            break
        ####按值排序，取出值最小的节点
        u=min(vertexAttrMarginalGain.items(),key=lambda x:x[1])[0]
        deletedCount+=1
        Hi.remove_node(u)
        '5.2: 确定删除节点后还能保持requireK'
        deletedVtmp = []  # 存删除的节点
        deletedVtmp.append(u)
        '这里可能会出现为了保持k-core需要删除查询点的情况，那就直接终止？'
        kcoreMaintain(Hi, requireK, deletedVtmp, queryVertexes)
        interSecttmp = [val for val in deletedVtmp if val in queryVertexes]  ##看需要删除的节点和查询节点是否由交集
        if len(interSecttmp) > 0:
            break
        ##可能删完就变成空的了;或者##删除完了不连通或者删除到查询节点就删除
        if not Hi or not isConnectedinG(queryVertexes,Hi):  ##
            break
        deletedCount +=  len(deletedVtmp) - 1
        for v in deletedVtmp:
            deletedVertexes.append(v)  # 更新删除的节点
        '5.3:更新相关的属性得分'
        for v in deletedVtmp:
            ###统计受影响的属性
            nattr = H.node[v]['attr']
            tmp = [val for val in nattr if val in queryAttributes]
            for w in tmp:
                VwList[w] = VwList[w] - 1
        print 'VwList:', VwList,'\tlen(Hi):',str(len(Hi))
        ###更新图属性得分
        scoretmp = sum([float(val * val) / float(len(Hi)) for val in VwList.itervalues()])
        graphAttrScores[deletedCount] = scoretmp
        ####更新节点属性得分
        vertexAttrMarginalGain = computeVertexAttrScore(Hi, VwList, queryAttributes, queryVertexes,requireK)
    '6:删除完了，找删除过程中子图属性分数最大的，还原子图'
    print 'deleted vertexes:', deletedVertexes
    print 'graphAttScores:', graphAttrScores

    '这里存在一个问题，可能会并列存在好几个最大值，那么应该取最后一个最大值，因为节点数最少（re:2017.3.2）'
    maxIndex=[]
    maxScore=max(graphAttrScores.items(),key=lambda x:x[1])[1]
    for key,score in graphAttrScores.items():
        if score==maxScore:
            maxIndex.append(key)
    index=maxIndex[-1] ##取最后一个等于最大值的
    for i in range(index):
        H.remove_node(deletedVertexes[i])
    return H

def kcoreMaintain(H,maxCoreness,deletedVs,queryVs):
    if H:
        '删除节点后，保持最小度至少是maxCoreness'
        '1:这里是找最小度'
        minIndex=H.nodes()[0] ##拥有最小度的节点
        mind=H.degree(minIndex) ##节点的度
        for n in nx.nodes_iter(H):
            if H.degree(n)<mind:
                mind=H.degree(n)
                minIndex=n
        '2:若当前最小度小于规定的度，则进行删除啊'
        if mind<maxCoreness:
            H.remove_node(minIndex)
            deletedVs.append(minIndex)
            kcoreMaintain(H,maxCoreness,deletedVs,queryVs)
    ##删除完不满足条件的节点后就可以返回了
    return


def computeVwList(queryAttrs,H):
    '计算子图中查询属性覆盖的节点个数'
    VwList={}
    VwList=VwList.fromkeys(queryAttrs,0) ##初始值默认是0
    for vertex in H.nodes():
        if H.node[vertex].has_key('attr') and H.node[vertex]['attr']!=None:
            for qa in queryAttrs:
                if qa in H.node[vertex]['attr']:
                    VwList[qa]+=1 ##频率加1
    return VwList

def computeVertexAttrScore(H,VwList,queryAttributes,queryVertexes,requireK):
    '计算除了查询节点外，每个节点在子图中的属性得分'
    vertexAttrScores={}
    for v in H.nodes():
        if v not in queryVertexes and H.node[v].has_key('attr'):
            vattrs=H.node[v]['attr']
            if vattrs is not None:
                interSectAttr=[val for val in queryAttributes if val in vattrs]
                score=sum([2.0*VwList[val]-1 for val in interSectAttr])
                vertexAttrScores[v]=score
            else:
                vertexAttrScores[v]=0
    '计算每个节点以及其邻居节点的属性得分，做attribute marginal gain'
    vertexAttrMarginalGain = {}
    degreesDict=nx.degree(H)
    for v in vertexAttrScores.keys():
        vertexAttrMarginalGain[v]=vertexAttrScores[v] ##先把自己的得分加上去
        for nei in nx.neighbors(H,v):
            if degreesDict[nei]==requireK-1:#把邻居中可能会被删除的节点的分数加上
                vertexAttrMarginalGain[v]+=vertexAttrScores[nei]
    return vertexAttrMarginalGain



def isConnectedinG(nodes,H):
    '判断给定的节点集合在子图中是否是连通的'
    '判断一个点到其他点否有路径即可'
    flag=True
    if len(nodes)>1:###节点集合个数至少大于1才可以
        source=nodes[0]
        for target in nodes[1:]:
            if not nx.has_path(H, source, target):
                flag = False
                return flag
    return flag


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

def testRetrieve():
    path = 'Data/'
    dataset = 'delicious'
    edgefile = path + dataset + '_graph'
    labelfile = path + dataset + '_nodelabel'
    queryVertexes = [1, 2, 3]  ##包含所有的查询节点
    queryAtts = ['2', '51']  ###包含所有的查询属性

    print 'Reading graph...'
    G = dataReader3(edgefile, labelfile)

    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root = shellIndex.root
    # #打印树
    # print 'Index Tree:'
    # shellIndex.displayTree(root,0)
    print  'querying...'
    qnodes = queryVertexes
    qattrs = queryAtts

    'CSM'
    # print 'retrieveCSM...'
    # resTNodes, H, maxCoreness = retrieveCSMV2(qnodes, shellIndex)
    # print 'csmNodes:', H.nodes()
    # print 'csmEdges:', H.edges()
    # print 'maxCoreness:', maxCoreness

    'CST'
    requireK=6
    print 'retrieveCST(k=',str(requireK),')...'
    resTNodes, H, maxCoreness = retrieveCSTV2(requireK,qnodes, shellIndex)
    print 'csTNodes:', H.nodes()
    print 'csTEdges:', H.edges()
    print 'maxCoreness:', maxCoreness

    Hi=greedyDecV2(H,requireK,qnodes,qattrs)
    print 'res:',Hi.nodes()

def toyTest():
    path = 'Data/'
    dataset = 'toy'
    edgefile = path + dataset + '-graph'
    labelfile = path + dataset + '-node'
    queryVertexes = [1, 2, 3]  ##包含所有的查询节点
    queryAtts = ['x', 'y']  ###包含所有的查询属性

    print 'Reading graph...'
    G = dataReader(edgefile, labelfile)

    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root = shellIndex.root
    # #打印树
    # print 'Index Tree:'
    # shellIndex.displayTree(root,0)
    print  'querying...'
    qnodes = queryVertexes
    qattrs = queryAtts

    'CST'
    requireK = 3
    print 'retrieveCST(k=', str(requireK), ')...'
    resnodes, H, maxCoreness = retrieveCSTV2(qnodes, shellIndex,requireK)
    if resnodes==None:
        print "This require k is too big."
        return
    print 'csTNodes:', H.nodes()
    print 'csTEdges:', H.edges()
    print 'maxCoreness:', maxCoreness

    Hi = greedyDecV2(H, requireK, qnodes, qattrs)
    print 'res:', Hi.nodes()



if __name__=='__main__':
    toyTest()








