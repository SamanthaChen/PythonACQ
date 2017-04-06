# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:OnlineProcessingV2.py
@time:2017/3/1020:42
@Function：在先查询方法的类（新修订版）
2017.3.16:修正CSMV2和CSTV2里面查找最低公共祖先哪里的一个致命错误
2017.3.30：
小修改，提高效率
改CSM，CST
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
    '3:从k-1层开始慢慢往上找(re:2017.3.16,修改了这一部分)'
    while k>=1:
        '2017.3.30：改为先判断'
        if (len(querys) == 0 and len(candiatelca) == 1):
            break
        ctmp = set()
        for tnode in candiatelca:  ##将k层候选节点的父母加进来(core大于等于k-1的树节点)
            ctmp.add(tnode.parent)
        for qv in queryVertexes:
            if coreDict[qv] == k - 1:  ##将k-1层的包含查询节点的树节点加进来
                ctmp.add(vertexTNodeList[qv])
                querys.remove(qv)
        candiatelca = ctmp ###这里应该不能用深拷贝？？？（re:2017.3.16）
        k = k - 1


    ###最低公共祖先应该是最后一个core等于k的
    lcaroot=list(candiatelca)[-1] ###(re:2017.3.15)
    for tnode in candiatelca:
        if tnode.core==k:
            lcaroot=tnode
    '5:找到最低lca后，BFS遍历树，返回所包含的所有图节点'
    queue=deque()
    queue.append(lcaroot)
    resvertexes=[] ##用列表是因为这里节点不会重复出现在多个shell
    while queue:
        tnode=queue.pop()
        resvertexes.extend(tnode.nodeList)
        if tnode.childList:
            queue.extend(tnode.childList)
    # print resvertexes
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
    while k>=1:
        if (len(querys) == 0 and len(candiatelca) == 1):
            break
        ctmp = set()
        for tnode in candiatelca:  ##将k层候选节点的父母加进来(core大于等于k-1的树节点)
            ctmp.add(tnode.parent)
        for qv in queryVertexes:
            if coreDict[qv] == k - 1:  ##将k-1层的包含查询节点的树节点加进来
                ctmp.add(vertexTNodeList[qv])
                querys.remove(qv)
        candiatelca = ctmp ###这里应该不能用深拷贝？？？（re:2017.3.16）
        k = k - 1

    ###最低公共祖先应该是最后一个core等于k的
    lcaroot = list(candiatelca)[-1]
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
    # print resvertexes
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
    # print 'VwList:', VwList, '\tlen(Hi):', str(len(Hi))
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
        tmpBreak=False
        for n in queryVertexes:
            if n in deletedVtmp: ##假设要删除的节点有查询节点，就直接退出
                tmpBreak=True
                break  ##跳出的是for循环
        if tmpBreak:
            print 'Ended in k-core maintance.'
            break ##跳出的是while循环
        '可能删完就变成空的了;或者##删除完了不连通或者删除到查询节点就删除'
        if not Hi or not isConnectedinG(queryVertexes,Hi):  ##
            print 'Ended in not connected.'
            break
        deletedCount +=  len(deletedVtmp) - 1
        ' 更新删除的节点'
        for v in deletedVtmp:
            deletedVertexes.append(v)  # 更新删除的节点
        '5.3:更新相关的属性得分'
        for v in deletedVtmp:
            ###统计受影响的属性
            if H.node[v].has_key('attr'):
                nattr = H.node[v]['attr']
                if nattr!=None:
                    for a in queryAttributes: ##遍历小的节省时间
                        if a in nattr:
                            VwList[a] = VwList[a] - 1

        # print 'VwList:', VwList,'\tlen(Hi):',str(len(Hi))
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

def kcoreMaintainFast(H,maxCoreness,deletedVs,queryVs):
    '2017.3.30:利用k-core分解'
    'line 245:list.remove(x): x not in list 不想改了'
    flag=True
    degreeDict=nx.degree(H)
    '按照度进行分组'
    degreeGroup=defaultdict(list)
    for v,k in degreeDict.items():
        degreeGroup[k].append(v)
    # maxk=max(degreeGroup.keys()) #最大的度
    mink=min(degreeGroup.keys()) #最小的度
    '一直删除节点直到不满足的点都删掉'
    deletedNodes=[]
    while mink<maxCoreness and len(degreeGroup)>0:
        group=copy.deepcopy(degreeGroup[mink])
        for v in group:
            if v not in deletedNodes:
                deletedNodes.append(v)
                degreeGroup[mink].remove(v)
            '要删除的点里面有查询节点'
            if v in queryVs:
                return False
            '删除的点的邻居度都减1'

            for w in nx.neighbors(H,v):
                if w not in deletedNodes:
                    oldk=degreeDict[w]
                    degreeDict[w]=oldk-1
                    degreeGroup[oldk].remove(w)
                    degreeGroup[oldk-1].append(w)
        '把空value的字典删掉'
        mink = min(degreeGroup.keys())  # 最小的度
        while len(degreeGroup[mink])==0:
            del degreeGroup[mink]
            mink = min(degreeGroup.keys())

    if deletedNodes:
        H.remove_nodes_from(deletedNodes)
    deletedVs.extend(deletedNodes)
    return flag



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
    '''
     '计算除了查询节点外，每个节点在子图中的属性得分'
     边缘属性得分=自己的属性得分+一度邻居中度==k-1的节点的属性得分。
     （这里只考虑一度邻居，实际上这个删除节点的影响会往下传播）
    :param H: 图
    :param VwList:
    :param queryAttributes:
    :param queryVertexes:
    :param requireK:
    :return:
    '''
    '计算除了查询节点外，每个节点在子图中的属性得分'
    vertexAttrScores={}
    for v in H.nodes():
        if v not in queryVertexes and H.node[v].has_key('attr'):
            vattrs=H.node[v]['attr']
            if vattrs is not None:
                score=0.0
                for val in queryAttributes: #一般来说QqueryAttr比较少，用作外循环（2017.3.30）
                    if val in vattrs:
                        score+=2.0*VwList[val]-1
                vertexAttrScores[v]=score
            else:
                vertexAttrScores[v]=0
    '计算每个节点以及其邻居节点的属性得分，做attribute marginal gain'
    vertexAttrMarginalGain = {}
    degreesDict=nx.degree(H) #度的字典
    for v in vertexAttrScores.keys():
        vertexAttrMarginalGain[v]=vertexAttrScores[v] ##先把自己的得分加上去
        for nei in nx.neighbors(H,v):
            if degreesDict[nei]==requireK-1:#把邻居中可能会被删除的节点的分数加上（这里只考虑一度邻居，实际上这个删除节点的影响会往下传播）
                vertexAttrMarginalGain[v]+=vertexAttrScores[nei]
    return vertexAttrMarginalGain



def isConnectedinG(nodes,H):
    '判断给定的节点集合在子图中是否是连通的'
    '判断一个点到其他点否有路径即可,这个是不是很耗时？'
    flag=True
    if len(nodes)>1:###节点集合个数至少大于1才可以
        source=nodes[0]
        for target in nodes[1:]:
            if not nx.has_path(H, source, target):
                flag = False
                return flag
    return flag


def greedyIncFromH(G,H,requireK,queryVertexs,queryAttrs,alpha):
    '以CSM/CST的结果（即输入的H）为候选集，先找一颗斯坦纳树保证连接，再局部扩张（扩张的节点从CSM/CST(re:改为原来的整张图)中选取）'
    '1.从候选图中找斯坦纳树'
    stG=buildSteinerTree(queryVertexs,H)
    # N=nx.number_of_nodes(stG) ##当前树的节点大小
    '当前解'
    solution=stG.nodes() ##当前解
    '2.局部搜索，同时计算子图得分'
    ####下面这两个先测试一下，后面看情况调整
    # graphAttSocre=[]
    # graphAttEntropy=[] ##用熵做子图属性分数
    # graphAttEntropy2=[]
    graphMinDegree=[]
    tmp=min(stG.degree().values())
    graphMinDegree.append(tmp) ##取最小度
    '当前最小度已经满足了，直接返回'
    if tmp>=requireK:
        print 'stG is qualified.'
        return stG
    # selectedNodes=[]   ###存每次选择的节点

    ###初始化连接类，初始化的同时已经在计算候选节点的分数了
    heuristic=LIHeuristic(H,stG,queryAttrs,alpha) ##初始化已经把srG的一度邻居的链接分数计算了 (节点的候选范围是G)（2017.3.30：候选范围改成H）
    # graphAttSocre.append(sum([val*val/float(N) for val in heuristic.VwList.values()]))
    # graphAttEntropy.append(sum([ entropy( val/float(N) ) for val in heuristic.VwList.values()]))
    # graphAttEntropy2.append(sum([  (val/float(N))*entropy(val / float(N)) for val in heuristic.VwList.values()]))
    # print 'connected：', heuristic.connectedScore
    # print 'attribute:', heuristic.attributeScore
    # print 'total:', heuristic.totalScore
    curNode=heuristic.getBestNode()##取出得分最高的
    # selectedNodes.append(curNode)
    # print 'curNode:',str(curNode)
    subgraph=nx.Graph()
    while curNode!=-1: ####扩张到没有候选节点或者到达最大coreness停止
        '加入结果集合'
        solution.append(curNode) ##最终结果集合包含的节点
        '更新子图'
        subgraph=G.subgraph(solution)
        # N=nx.number_of_nodes(subgraph)
        # graphAttSocre.append(sum([val*val / float(N) for val in heuristic.VwList.values()]))
        # graphAttEntropy.append(sum([entropy(val / float(N)) for val in heuristic.VwList.values()]))
        # graphAttEntropy2.append(sum([(val / float(N))*entropy(val / float(N)) for val in heuristic.VwList.values()]))
        '更新最小度'
        curMinDegree=min(subgraph.degree().values())
        graphMinDegree.append(curMinDegree)##取最小度
        if curMinDegree>=requireK:  ###到达最大度可以跳出
            print 'Ended in  mink>=k.'
            break
        '将当前节点的未访问邻居加入到queue(这里应该修改一下)'
        tmpaddNodes=[]
        for nei in H.neighbors(curNode): ####(re:2017.3.15 候选范围扩大到G)（2017.3.30：候选范围改成H）
            if (nei not in solution) and (nei not in heuristic.connectedScore.keys()):
                if H.degree(nei)>=requireK: #度大于指定k的才可以(2017.3.30)（2017.3.30：候选范围改成H）
                    tmpaddNodes.append(nei)
        '批量加候选节点'
        if len(tmpaddNodes)>0:
            heuristic.addNodeList(tmpaddNodes,solution)

        # print 'connected：', heuristic.connectedScore
        # print 'attribute:', heuristic.attributeScore
        # print 'total:', heuristic.totalScore
        '继续获取最优节点'
        curNode=heuristic.getBestNode()
        # selectedNodes.append(curNode)
        # print 'curNode:',str(curNode)
    if curNode==-1:
        print 'Ended in no candiate.'
    print 'graphMinDegree:',graphMinDegree
    # print 'graphAttSocre:',graphAttSocre
    # print 'graphAttEntropy:',graphAttEntropy
    # print 'graphAttEntropy2:', graphAttEntropy2
    # print 'selectedNodes:',selectedNodes
    # subgraph=G.subgraph(solution)
    return subgraph

def greedyIncFromG(G,H,requireK,queryVertexs,queryAttrs,alpha):
    '以CSM/CST的结果（即输入的H）为候选集，先找一颗斯坦纳树保证连接，再局部扩张（扩张的节点从CSM/CST(re:改为原来的整张图)中选取）'
    '1.从候选图中找斯坦纳树'
    stG=buildSteinerTree(queryVertexs,H)
    # N=nx.number_of_nodes(stG) ##当前树的节点大小
    '当前解'
    solution=stG.nodes() ##当前解
    '2.局部搜索，同时计算子图得分'
    ####下面这两个先测试一下，后面看情况调整
    # graphAttSocre=[]
    # graphAttEntropy=[] ##用熵做子图属性分数
    # graphAttEntropy2=[]
    graphMinDegree=[]
    graphMinDegree.append(min(stG.degree().values())) ##取最小度
    # selectedNodes=[]   ###存每次选择的节点

    ###初始化连接类，初始化的同时已经在计算候选节点的分数了
    heuristic=LIHeuristic(G,stG,queryAttrs,alpha) ##初始化已经把srG的一度邻居的链接分数计算了 (节点的候选范围是G)（2017.3.30：候选范围改成H）
    # graphAttSocre.append(sum([val*val/float(N) for val in heuristic.VwList.values()]))
    # graphAttEntropy.append(sum([ entropy( val/float(N) ) for val in heuristic.VwList.values()]))
    # graphAttEntropy2.append(sum([  (val/float(N))*entropy(val / float(N)) for val in heuristic.VwList.values()]))
    # print 'connected：', heuristic.connectedScore
    # print 'attribute:', heuristic.attributeScore
    # print 'total:', heuristic.totalScore
    curNode=heuristic.getBestNode()##取出得分最高的
    # selectedNodes.append(curNode)
    # print 'curNode:',str(curNode)
    subgraph=nx.Graph()
    while curNode!=-1: ####扩张到没有候选节点或者到达最大coreness停止
        '加入结果集合'
        solution.append(curNode) ##最终结果集合包含的节点
        '更新子图'
        subgraph=G.subgraph(solution)
        # N=nx.number_of_nodes(subgraph)
        # graphAttSocre.append(sum([val*val / float(N) for val in heuristic.VwList.values()]))
        # graphAttEntropy.append(sum([entropy(val / float(N)) for val in heuristic.VwList.values()]))
        # graphAttEntropy2.append(sum([(val / float(N))*entropy(val / float(N)) for val in heuristic.VwList.values()]))
        '更新最小度'
        curMinDegree=min(subgraph.degree().values())
        graphMinDegree.append(curMinDegree)##取最小度
        if curMinDegree>=requireK:  ###到达最大度可以跳出
            print 'Ended in  mink>=k.'
            break
        '将当前节点的未访问邻居加入到queue(这里应该修改一下)'
        tmpaddNodes=[]
        for nei in G.neighbors(curNode): ####(re:2017.3.15 候选范围扩大到G)（2017.3.30：候选范围改成H）
            if (nei not in solution) and (nei not in heuristic.connectedScore.keys()):
                if G.degree(nei)>=requireK: #度大于指定k的才可以(2017.3.30)（2017.3.30：候选范围改成H）
                    tmpaddNodes.append(nei)
        '批量加候选节点'
        if len(tmpaddNodes)>0:
            heuristic.addNodeList(tmpaddNodes,solution)

        # print 'connected：', heuristic.connectedScore
        # print 'attribute:', heuristic.attributeScore
        # print 'total:', heuristic.totalScore
        '继续获取最优节点'
        curNode=heuristic.getBestNode()
        # selectedNodes.append(curNode)
        # print 'curNode:',str(curNode)

    if curNode==-1:
        print 'Ended in no candiate.'

    print 'graphMinDegree:',graphMinDegree
    # print 'graphAttSocre:',graphAttSocre
    # print 'graphAttEntropy:',graphAttEntropy
    # print 'graphAttEntropy2:', graphAttEntropy2
    # print 'selectedNodes:',selectedNodes
    # subgraph=G.subgraph(solution)
    return subgraph

def entropy(p):
    '熵的计算'
    return -p*log(p,2)

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
    queryVertexes = [1, 5]  ##包含所有的查询节点
    queryAtts = ['x', 'y']  ###包含所有的查询属性

    print 'Reading graph...'
    G = dataReader(edgefile, labelfile)

    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root = shellIndex.root
    # #打印树
    print 'Index Tree:'
    shellIndex.displayTree(root,0)
    print  'querying...'
    qnodes = queryVertexes
    qattrs = queryAtts

    # 'CST'
    # requireK = 1
    # print 'retrieveCST(k=', str(requireK), ')...'
    # resnodes, H, maxCoreness = retrieveCSTV2(qnodes, shellIndex, requireK)

    'CSM'
    resnodes,H,maxCoreness=retrieveCSMV2(queryVertexes,shellIndex)

    if resnodes==None:
        print "This require k is too big."
        return
    print 'csTNodes:', H.nodes()
    print 'csTEdges:', H.edges()
    print 'maxCoreness:', maxCoreness

    Hi = greedyIncFromH(G,H, maxCoreness, qnodes, qattrs,0.0)
    print 'res:', Hi.nodes()



if __name__=='__main__':
    toyTest()










