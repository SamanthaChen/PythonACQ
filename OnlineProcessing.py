# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:OnlineProcessing.py
@time:2017/2/2611:12
@在线查询的方法类,
"""
import networkx as nx
import copy
from math import log
from ShellStructIndex import ShellStructIndex as ShellIndex
from collections import defaultdict
import matplotlib.pyplot as plt
import Queue
from SteinTree import *
from LIHeuristic import LIHeuristic

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

def retrieveCSM(queryVertexes,index):
    '根据索引，找到包含查询节点的core最大的子图'
    queryVertexesCopy=copy.deepcopy(queryVertexes)#复制一个新的，因为后面要删除
    qVcopy=copy.deepcopy(queryVertexesCopy)
    vertexTNodeList=index.vertexTNodelist ##先把图节点到树节点的映射拿出来
    '自底向上，一层层往上找，最终的查询节点会汇聚到一个最低的公共祖先'
    '步骤1：计算查询节点集合中最大的coreness'
    maxQCore = 0
    for query in queryVertexesCopy:
        if index.coreDict[query]>maxQCore:
            maxQCore=index.coreDict[query]
    '步骤2:从底层开始往上找最低公共祖先'
    csmTNodes=[] #存储的是包含查询节点的csm候选树节点集合（要不要改成图节点啊）
    candinateTNodes=set() ###包含查询节点和所有的候选节点
    k=maxQCore
    flag=False
    while not ((len(candinateTNodes)==1) and (len(queryVertexesCopy)==0)):
        '2.1：筛选core=k的节点（1.query节点集里2.候选节点集里）'
        vk=[]
        vk=filter(lambda x:vertexTNodeList[x].core==k,queryVertexesCopy) #1.query节点里面core=k的节点
        tk=[]
        if candinateTNodes:
            tk=filter(lambda y:y.core==k,candinateTNodes) #2.候选树节点里面core=k的节点
        '步骤2.2：ccore-k的节点加入结果集，其父母加入候选节点集'
        alltk=set() ##这一层的所有候选节点
        if vk:
            for v in vk:
                alltk.add(vertexTNodeList[v])
                candinateTNodes.add(vertexTNodeList[v].parent) #这一层查询节点的父母也做候选集合
                queryVertexesCopy.remove(v) #查询节点访问过了就删除
        if tk:
            for t in tk:
                alltk.add(t)
                candinateTNodes.add(t.parent)
                candinateTNodes.remove(t) #候选节点访问过了就删除，但是需要把候选节点的父母加上
        for tt in alltk:
            csmTNodes.append(tt)
        k=k-1
        '步骤2.3：判断最后一个lca是否需要加入到节点集里面'
        ##增加的一个标志位,为了判断最后的lca要不要加入到结果中区(2017.2.27)
        if len(alltk)==1 and len(candinateTNodes)==1 and (not queryVertexesCopy):
            flag=True
    # ###把最后的lca也加入最终结果??
    if not flag:
        csmTNodes.append(list(candinateTNodes)[0])
    ###获得最大最小度
    maxCoreness=csmTNodes[-1].core
    '步骤3：根据树节点，重新构建子图H*'
    resVertexes=[]
    for tnode in csmTNodes:
        for v in tnode.nodeList:
            resVertexes.append(v)
    H=ShellIndex.G.subgraph(resVertexes) #根据包含的节点获得子图，但是不包含节点属性
    return csmTNodes,H,maxCoreness

def retrieveCST(queryVertexes,index,givenk):
    '类似于CSM的结果中获得CST(k)的结果'
    '根据索引，找到包含查询节点的core最大的子图'
    queryVertexesCopy=copy.deepcopy(queryVertexes)#复制一个新的，因为后面要删除
    vertexTNodeList=index.vertexTNodelist ##先把图节点到树节点的映射拿出来
    '自底向上，一层层往上找，最终的查询节点会汇聚到一个最低的公共祖先'
    '步骤1：计算查询节点集合中最大的coreness'
    maxQCore = 0
    for query in queryVertexesCopy:
        if index.coreDict[query]>maxQCore:
            maxQCore=index.coreDict[query]
    '步骤2:从底层开始往上找最低公共祖先'
    csmTNodes=[] #存储的是包含查询节点的csm候选树节点集合（要不要改成图节点啊）
    candinateTNodes=set() ###包含查询节点和所有的候选节点
    k=maxQCore
    flag=False
    while not ((len(candinateTNodes)==1) and (len(queryVertexesCopy)==0)):
        '2.1：筛选core=k的节点（1.query节点集里2.候选节点集里）'
        vk=[]
        vk=filter(lambda x:vertexTNodeList[x].core==k,queryVertexesCopy) #1.query节点里面core=k的节点
        tk=[]
        if candinateTNodes:
            tk=filter(lambda y:y.core==k,candinateTNodes) #2.候选树节点里面core=k的节点
        '步骤2.2：ccore-k的节点加入结果集，其父母加入候选节点集'
        alltk=set() ##这一层的所有候选节点
        if vk:
            for v in vk:
                alltk.add(vertexTNodeList[v])
                candinateTNodes.add(vertexTNodeList[v].parent) #这一层查询节点的父母也做候选集合
                queryVertexesCopy.remove(v) #查询节点访问过了就删除
        if tk:
            for t in tk:
                alltk.add(t)
                candinateTNodes.add(t.parent)
                candinateTNodes.remove(t) #候选节点访问过了就删除，但是需要把候选节点的父母加上
        for tt in alltk:
            csmTNodes.append(tt)
        k=k-1
        '步骤2.3：判断最后一个lca是否需要加入到节点集里面'
        ##增加的一个标志位,为了判断最后的lca要不要加入到结果中区(2017.2.27)
        if len(alltk)==1 and len(candinateTNodes)==1 and (not queryVertexesCopy):
            flag=True
    # ###把最后的lca也加入最终结果??
    if not flag:
        csmTNodes.append(list(candinateTNodes)[0])
    ###获得最大最小度
    maxCoreness=csmTNodes[-1].core
    #####重新设置这两个变量
    lowCoreness=maxCoreness
    highCoreness=maxQCore
    '步骤3：从LCA开始往上找，一直找到k'
    tmpCoreness=lowCoreness
    tmpNode=csmTNodes[-1] ##最顶上的树节点
    while tmpCoreness>givenk and tmpNode.parent:
        csmTNodes.append(tmpNode.parent)
        tmpNode=tmpNode.parent
        tmpCoreness=tmpNode.core
    '步骤4:BFS,把所有候选树节点的孩子节点全都加进来'
    lcaTNode=csmTNodes[-1]
    candTNodeSet=[]
    queue=[]
    queue.append(lcaTNode)
    ###BFS
    while len(queue)>0:
        curTNode=queue[0]
        candTNodeSet.append(curTNode)
        queue.remove(curTNode)
        if curTNode.childList:
            for child in curTNode.childList:
                queue.append(child)

    '步骤5：把树节点包含的所有的图节点加入到结果集合'
    resVertexes=[]
    for tnode in candTNodeSet:
        for v in tnode.nodeList:
            resVertexes.append(v)
    resH=index.G.subgraph(resVertexes) #根据包含的节点获得子图，但是不包含节点属性
    return resH



def computeGAttrScore(H,attrNodeDict):
    '计算子图的属性分数'
    HAttrSocre=0
    N=nx.number_of_nodes(H)
    for value in attrNodeDict.itervalues():
        HAttrSocre+=float(len(value))/float(N)
    return HAttrSocre

def computeVAttrScore(H,VwList,queryAttributes,queryVertexes):
    '计算节点的属性分数'
     ##(re:2017.3.2 nodeAttScore改成字典)
    nodeAtteSocreDict={}
    for n in nx.nodes_iter(H):
        if n not in queryVertexes:####不计算查询节点的分数
            nattr=H.node[n]['attr']
            if nattr is not None:
                tmp=[val for val in nattr if val in queryAttributes]  #计算节点属性与查询属性的交集
                score=sum([2.0*VwList[val]-1 for val in tmp])
                nodeAtteSocreDict[n]=score
            else:
                nodeAtteSocreDict[n]=0
    return nodeAtteSocreDict

def greedyDec(H,maxCoreness,queryVertexes,queryAttributes):
    '贪婪算法：每次循环删除一个属性分数最小的节点'
    '1:先获得初始的候选子图'
    Hi=copy.deepcopy(H) #先深拷贝一个子图
    N=nx.number_of_nodes(Hi) #子图的节点个数
    deletedVertexes=[] #存放删除的节点
    graphAttScores=[None]*(N+1) #存放删除对应节点后的子图分数
    '2:计算查询属性的倒排'
    attrNodeDict=computeInvertedAttr(H,queryAttributes)
    VwList={}###属性w<-->含有w的节点个数
    for key,value in attrNodeDict.items():
        VwList[key]=len(value) #(w,Vw个数)
    print 'VwList:',VwList
    '3:计算图的属性分数'
    HAttrSocre=sum([float(val)* float(val)/float(N) for val in VwList.itervalues()])
    graphAttScores[0]=HAttrSocre
    '4:计算节点的属性分数'
    nodeAtteSocreDict=computeVAttrScore(Hi,VwList,queryAttributes,queryVertexes)
    '5:循环删除节点'
    deletCount=0# 删除的节点计数
    while Hi and nx.is_connected(Hi):
        '5.1:删除查询节点外属性得分最小的节点'
        if not nodeAtteSocreDict: ###可能会出现除了查询节点，其他点都删完了
            break
        u=min(nodeAtteSocreDict.items(),key=lambda x:x[1])[0] #最小score对应的节点
        deletCount+=1
        Hi.remove_node(u) #删除节点
        '5.2:确定删除后最小度仍能保持最小度'
        deletedVtmp=[] #存删除的节点
        deletedVtmp.append(u)
        '这里可能会出现为了保持k-core需要删除查询点的情况，那就直接终止？'
        kcoreMaintain(Hi,maxCoreness,deletedVtmp,queryVertexes)
        interSecttmp=[val for val in deletedVtmp if val in queryVertexes] ##看需要删除的节点和查询节点是否由交集
        if len(interSecttmp)>0:
            break
        ##可能删完就变成空的了;或者##删除完了不连通或者删除到查询节点就删除
        if not Hi or  not nx.is_connected(Hi): ##
            break
        deletCount=deletCount+len(deletedVtmp)-1
        for v in deletedVtmp:
            deletedVertexes.append(v) #更新删除的节点
        '5.3:更新相关的属性得分'
        for v in deletedVtmp:
            ###统计受影响的属性
            nattr=H.node[v]['attr']
            tmp=[val for val in nattr if val in queryAttributes]
            for w in tmp:
                VwList[w]=VwList[w]-1
        print 'VwList:',VwList
        ###更新图属性得分
        N=nx.number_of_nodes(Hi)
        HAttrSocre=sum([float(val)* float(val)/float(N) for val in VwList.itervalues()])
        graphAttScores[deletCount]=HAttrSocre
        ####更新节点属性得分
        nodeAtteSocreDict=computeVAttrScore(Hi,VwList,queryAttributes,queryVertexes)
    '6:删除完了，找删除过程中子图属性分数最大的，还原子图'
    print 'deleted vertexes:',deletedVertexes
    print 'graphAttScores:',graphAttScores
    '这里存在一个问题，可能会并列存在好几个最大值，那么应该取最后一个最大值，因为节点数最少（re:2017.3.2）'
    maxScore=max(graphAttScores)
    maxIndex=[]
    i=0##索引
    for score in graphAttScores:
        if score==maxScore:
            maxIndex.append(i)
        i+=1
    index=maxIndex[-1] ##取最后一个等于最大值的
    for i in range(index):
        H.remove_node(deletedVertexes[i])
    return H


def kcoreMaintain(H,maxCoreness,deletedVs,queryVs):
    if H:
        '删除节点后，保持最小度至少是maxCoreness'
        ###这里是找最小度
        mind=H.degree(H.nodes()[0])
        minIndex=H.nodes()[0]
        for n in nx.nodes_iter(H):
            if H.degree(n)<mind:
                mind=H.degree(n)
                minIndex=n
        ###若当前最小度小于规定的度，则进行删除啊
        if mind<maxCoreness:
            H.remove_node(minIndex)
            deletedVs.append(minIndex)
            kcoreMaintain(H,maxCoreness,deletedVs,queryVs)
    ##删除完不满足条件的节点后就可以返回了
    return

def computeInvertedAttr(G,queryAttrs):
    '计算查询节点属性的倒排'
    attrNodeDict=defaultdict(list) #<属性，节点集合>
    for id in nx.nodes_iter(G):
        # print 'id:',str(id),G.node[id]
        ####################可能存在有节点但是没有属性(2017.3.4)###############
        if G.node[id].has_key('attr'):
            if G.node[id]['attr'] is not None: ##判断是不是等于None
                for attr in  G.node[id]['attr']:
                        if attr in queryAttrs:
                            attrNodeDict[attr].append(id)
    return attrNodeDict

from RankNode import RankNode
import Queue
def greedyConnection(H,maxCoreness,queryVertexes,queryAttributes):
    '从CSM的结果开始，对搜索空间添加节点直到连通(2017.3.5)'
    '1:查询节点加入'
    H=nx.Graph()  #####后面记得删这句
    N=nx.number_of_nodes(H)
    resNodeSet=set()
    resG=nx.Graph()
    ###用一个字典存结果集中的度
    resNodeDegreeDict={}
    resMinD=N
    ####度列表
    degreeDict={}
    for i in range(maxCoreness+1):
        degreeDict[i]=[]
    ###初始化属性集列表
    VwList={}
    for qa in queryAttributes:
        VwList[qa]=0

    '2:计算查询属性的倒排'
    attrNodeDict=computeInvertedAttr(H,queryAttributes)
    '3:扩张'
    connectAttScoreDict={}
    queue=[]
    for q in queryVertexes:##将查询节点入队，优先级设为无穷大
        qrank=RankNode(q,float("inf"),0)
        queue.append(qrank)
    while not queue:
        curNode=sorted(queue).pop(0)
        resNodeSet.add(curNode)
        resG=H.subgraph(resNodeSet) ###费时吗？
        '更新最小度'
        if nx.is_connected(resG) and resMinD>=maxCoreness:
            break
        for nei in H.neighbors(curNode):
            if (nei not in resNodeSet) and (nei not in queue):
                '计算连通分数'
                interSectN=[val for val in H.neighbors(nei) if val in resNodeSet]
                conScore=len(interSectN)
                '计算属性得分'
                attScore=0
                if  H.node[q]['attr'] is not None:
                    interSectA=[val for val in H.node[nei]['attr'] if val in queryAttributes]
                    for a in interSectN:
                        attScore+=2.0*(VwList[a]+1)-1
                '加入队列'
                queue.append(RankNode(nei,conScore,attScore))



def csmSTTree11111(H,maxCoreness,queryVertexs,queryAttrs,alpha):
    '以CSM的结果为候选集，先找一颗斯坦纳树，再局部扩张'
    iteration=len(H)-len(queryVertexs)  ###最大迭代次数
    '1.从候选图中找斯坦纳树'
    stG=buildSteinerTree(queryVertexs,H)
    solution=stG.nodes() ##当前解
    '2.局部搜索，同时计算子图得分'
    ####下面这两个先测试一下，后面看情况调整
    graphAttSocre=[None]*(iteration+1)
    graphMinDegree=[None]*(iteration+1)
    graphMinDegree[0]=min(stG.degree(),key=lambda x:x[1]) ##取最小度
    #####统计一下原来的查询属性的频率
    VwList={} ##子图中对应查询属性覆盖的节点数
    VwList.fromkeys(queryAttrs,0)###批量初始化
    for qa in queryAttrs:
        for node in stG:
            if stG.node[node].has_key('attr') and stG.node[node]['attr']!=None:
                for na in stG.node[node]['attr']:
                    if na==qa:
                        VwList[qa]+=1
    graphAttSocre[0]=[val*val/float(len(stG)) for val in VwList]
    ###先算一下当前一度邻居
    queue=Queue.PriorityQueue()  ##创建一个优先队列(注意优先队列默认是小到大)
    ###初始化连接类
    connection=LIHeuristic(H,stG.nodes()) ##初始化已经把srG的一度邻居的链接分数计算了
    neighbors=connection.nodeGroup.keys() ##
    ####计算一下当前一度邻居的分数，并放入队列
    aScore={}
    aScore.fromkeys(neighbors,0.0)
    cScore={}
    cScore.fromkeys(neighbors,0.0)
    totalScore={}
    totalScore.fromkeys(neighbors,0.0)
    maxaScore=0
    maxcScore=0
    for n in neighbors:
        ####计算连接分数
        cScore[n]=connection.nodeGroup[n] #连接个数
        if cScore[n]>maxcScore:
            maxcScore=cScore[n]
        #####计算属性得分
        if H.node[n].has_key('attr') and H.node[n]['attr']!=None:
            for a in H.node[n]['attr']:
                if a in queryAttrs:
                    aScore[n]+=2*VwList[a]-1
        if aScore[n]>maxaScore:
            maxcScore=aScore[n]
    ###最后归一化计算总分数
    visitedNodes=[]
    visitedNodes.addAll(stG.nodes())  ##存所有访问过的节点
    for n in neighbors:
        tmp=alpha*(cScore[n]/maxcScore)+(1-alpha)(aScore[n]/maxaScore)
        totalScore[n]=tmp
        queue.put((-tmp,n))
    count=1
    while not queue.empty():
        ##取出得分最高的
        curNode=queue.get(0)
        ###加入结果集合
        solution.append(curNode)
        visitedNodes.append(curNode)
        ##更新VwList
        if H.node[n].has_key('attr') and H.node[n]['attr']!=None:
            for a in H.node[n]['attr']:
                if a in queryAttrs:
                    VwList[a]+=1
        ###更新子图属性得分
        graphAttSocre[count]=[val*val/float(len(stG)) for val in VwList]
        ###更新最小度（后面记得删掉，太耗时间）
        subgraph=H.subgraph(solution)
        graphMinDegree[0]=min(subgraph.degree(),key=lambda x:x[1]) ##取最小度
        count+=1
        ####将当前节点的未访问邻居加入到queue
        # for nei in H.neighbors(curNode):
            # if nei not in solution:

def csmSTTree(H,maxCoreness,queryVertexs,queryAttrs,alpha):
    '以CSM的结果为候选集，先找一颗斯坦纳树，再局部扩张'
    '1.从候选图中找斯坦纳树'
    stG=buildSteinerTree(queryVertexs,H)
    N=nx.number_of_nodes(stG)
    solution=stG.nodes() ##当前解
    '2.局部搜索，同时计算子图得分'
    ####下面这两个先测试一下，后面看情况调整
    graphAttSocre=[]
    graphAttEntropy=[] ##用熵做子图属性分数
    graphAttEntropy2=[]
    graphMinDegree=[]
    graphMinDegree.append(min(stG.degree().items(),key=lambda x:x[1])[1]) ##取最小度
    selectedNodes=[]

    ###初始化连接类
    heuristic=LIHeuristic(H,stG,queryAttrs,alpha) ##初始化已经把srG的一度邻居的链接分数计算了
    graphAttSocre.append(sum([val*val/float(N) for val in heuristic.VwList.values()]))
    graphAttEntropy.append(sum([ entropy( val/float(N) ) for val in heuristic.VwList.values()]))
    graphAttEntropy2.append(sum([  (val/float(N))*entropy(val / float(N)) for val in heuristic.VwList.values()]))
    # print 'connected：', heuristic.connectedScore
    # print 'attribute:', heuristic.attributeScore
    # print 'total:', heuristic.totalScore
    curNode=heuristic.getBestNode()##取出得分最高的
    selectedNodes.append(curNode)
    # print 'curNode:',str(curNode)


    while curNode!=-1: ####扩张到没有候选节点或者到达最大coreness停止
        ###加入结果集合
        solution.append(curNode) ##最终结果集合包含的节点
        ###更新子图属性得分
        subgraph=H.subgraph(solution)
        N=nx.number_of_nodes(subgraph)
        graphAttSocre.append(sum([val*val / float(N) for val in heuristic.VwList.values()]))
        graphAttEntropy.append(sum([entropy(val / float(N)) for val in heuristic.VwList.values()]))
        graphAttEntropy2.append(sum([(val / float(N))*entropy(val / float(N)) for val in heuristic.VwList.values()]))
        ###更新最小度（后面记得删掉，太耗时间）
        graphMinDegree.append(min(subgraph.degree().items(),key=lambda x:x[1])[1]) ##取最小度
        if graphMinDegree[-1]==maxCoreness:
            break
        ####将当前节点的未访问邻居加入到queue
        for nei in H.neighbors(curNode):
            if (nei not in solution) and (nei not in heuristic.nodeGroup.keys()):
                if H.degree(nei)>maxCoreness:
                    heuristic.addNode(nei,solution)

        # print 'connected：', heuristic.connectedScore
        # print 'attribute:', heuristic.attributeScore
        # print 'total:', heuristic.totalScore
        curNode=heuristic.getBestNode()
        selectedNodes.append(curNode)
        # print 'curNode:',str(curNode)

    print 'graphMinDegree:',graphMinDegree
    print 'graphAttSocre:',graphAttSocre
    print 'graphAttEntropy:',graphAttEntropy
    print 'graphAttEntropy2:', graphAttEntropy2
    print 'selectedNodes:',selectedNodes
    subgraph=H.subgraph(H)
    return subgraph

def entropy(p):
    '熵的计算'
    return -p*log(p,2)

def displayTree(root,level):
    '打印树'
    string=""
    if root:
        #前置的空格
        preStr=""
        for i in range(level):
            preStr=preStr+" "
        string=string+preStr+"--(core:"+str(root.core)+") {"
        #root包含的图节点
        for node in root.nodeList:
            string=string+str(node)+", "
        string=string+"}"
        print string

        #打印孩子节点
        if root.childList:
            for chid in root.childList:
                displayTree(chid,level+1)

def dataReader2(edgefile,attrfile):
    '读的是delicious类型的数据'
    G=nx.read_edgelist(edgefile,nodetype=int) #从邻接表读取图数据
    #读取节点的属性文件
    f=open(attrfile)
    for line in f.readlines():
        line=line.strip('\n')
        words=line.split() ##第一个是id，后面跟着的都是属性
        id=int(words[0])
        attr=words[1]
        if G.has_node(id):
            if G.node[id].has_key('attr'):
                G.node[id]['attr'].append(attr)
            else:
                G.node[id]['attr']=[] #新加一个列表
    return G

def dataReader3(adjlistFile,attrFile):
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

def dataReader4(adhListFile,attrFile):
    '处理节点不连续的文件'
def test():
    ################      TEST 1     ###############################
    graphFile='Data/toy-graph'
    nodeFile='Data/toy-node'
    G=dataReader(graphFile,nodeFile)
    print 'ok'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root=shellIndex.root
    #打印树
    # displayTree(root,0)
    queryVertexes=[1,3]
    resTNodes,H,maxCoreness =retrieveCSM(queryVertexes,shellIndex)
    print 'csm:',H.nodes()
    print 'maxCoreness:',maxCoreness
    ###假设没有指定查询属性，取查询节点属性的交集
    queryAttributes=['tree','algorithm']
    H1=greedyDec(H,3,queryVertexes,queryAttributes)
    print 'final res:',H1.nodes()

    ###################   TEST 2   ##############################
    edgefile='Data/delicious_graph'
    labelfile='Data/delicious_nodelabel'

    print 'Reading graph...'
    G=dataReader3(edgefile,labelfile)

    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root=shellIndex.root
    # #打印树
    # print 'Index Tree:'
    # displayTree(root,0)

    queryVertex=[130,119,149,215]
    queryAttr=['205','158','28']

    print 'retrieveCSM...'
    resTNodes,H,maxCoreness =retrieveCSM(queryVertex,shellIndex)
    print 'csm:',H.nodes()
    print 'maxCoreness:',maxCoreness

    print 'querying...'
    H1=greedyDec(H,10,queryVertex,queryAttr)
    print 'final res:',H1.nodes()


def runcsmGrD():
    ###############################################################################
    ####      读query文件，并将结果输出（注意结果文件与query文件相对应）###########
    ###############################################################################
    path='L:/ACQData/'
    dataset='texas'
    algo='grdec/'
    edgefile=path+'inputfile/'+dataset+'_graph'
    labelfile=path+'inputfile/'+dataset+'_nodelabel'
    queryfile=path+dataset+'_Query_wall.txt'
    outfile=path+algo+dataset+'_Query_wall_csm_res.txt'
    queryVertexes=[] ##包含所有的查询节点
    queryAtts=[] ###包含所有的查询属性
    fq=open(queryfile,'r')
    lineCount=0
    for line in fq.readlines():
        lineCount+=1
        line=line.strip("\n") #把末尾换行符去掉
        words=line.split('\t')

        nodeStartid=words.index('node:')  ####查询节点开始的位置
        attrsStartid=words.index('attrs:') ####查询属性开始的位置

        tmp=words[nodeStartid+1:attrsStartid]
        if(len(tmp)==0):  #####可能会出现查询节点为空
            break
        nodeList=[]
        for val in tmp:
            if val:
                nodeList.append(int(val))
        queryVertexes.append(nodeList)

        attrList=words[attrsStartid+1:] ###选择所以关键词
        attrList[-1].strip('\n')  ##去不掉最后一个换行符。。
        queryAtts.append(attrList)

    fq.close()


    print 'Reading graph...'
    G=dataReader3(edgefile,labelfile)

    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root=shellIndex.root
    # #打印树
    # print 'Index Tree:'
    # displayTree(root,0)


    wf=open(outfile,'w')
    for i in range(lineCount):
        print '**************************************************************************'
        print 'NO.'+str(i)+' querying...'
        qnode=queryVertexes[i]
        qattr=queryAtts[i]
        print 'retrieveCSM...'
        resTNodes,H,maxCoreness =retrieveCSM(qnode,shellIndex)
        print 'csm:',H.nodes()
        print 'maxCoreness:',maxCoreness
        Hi=greedyDec(H,maxCoreness,qnode,qattr)
        print 'final res:',Hi.nodes()
        ####文件输出
        string=''
        for node in Hi.nodes():
            string+=str(node)+' ' ####空格分割
        wf.write(string+'\n')
        print '**************************************************************************'
    wf.close()

def outPutcsm():
    path='L:/ACQData/'
    dataset='dblps'
    algo='csm/'
    edgefile=path+'inputfile/'+dataset+'_graph'
    labelfile=path+'inputfile/'+dataset+'_nodelabel'
    queryfile=path+dataset+'_Query_wall.txt'
    outfile=path+algo+dataset+'_Query_wall_CSMnode.txt'
    queryVertexes=[] ##包含所有的查询节点
    queryAtts=[] ###包含所有的查询属性
    fq=open(queryfile,'r')
    lineCount=0
    for line in fq.readlines():
        lineCount+=1
        line=line.strip("\n") #把末尾换行符去掉
        words=line.split('\t')

        nodeStartid=words.index('node:')  ####查询节点开始的位置
        attrsStartid=words.index('attrs:') ####查询属性开始的位置

        tmp=words[nodeStartid+1:attrsStartid]
        if(len(tmp)==0):  #####可能会出现查询节点为空
            break
        nodeList=[]
        for val in tmp:
            if val:
                nodeList.append(int(val))
        queryVertexes.append(nodeList)

        attrList=words[attrsStartid+1:] ###选择所以关键词
        attrList[-1].strip('\n')  ##去不掉最后一个换行符。。
        queryAtts.append(attrList)

    fq.close()


    print 'Reading graph...'
    G=dataReader3(edgefile,labelfile)

    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root=shellIndex.root
    # #打印树
    # print 'Index Tree:'
    # displayTree(root,0)

    wf=open(outfile,'w')
    for i in range(lineCount):
        print '**************************************************************************'
        print 'NO.'+str(i)+' querying...'
        qnode=queryVertexes[i]
        qattr=queryAtts[i]
        print 'retrieveCSM...'
        resTNodes,H,maxCoreness =retrieveCSM(qnode,shellIndex)
        print 'csm:',H.nodes()
        print 'maxCoreness:',maxCoreness

        ####文件输出
        string=''
        for node in H.nodes():
            string+=str(node)+' ' ####空格分割
        wf.write(string+'\n')
        print '**************************************************************************'
    wf.close()

def runcstGrd():
      ###############################################################################
    ####      读query文件，并将结果输出（注意结果文件与query文件相对应）###########
    ###############################################################################
    path='L:/ACQData/'
    dataset='delicious'
    algo='cstGrd/'
    k=8
    edgefile=path+'inputfile/'+dataset+'_graph'
    labelfile=path+'inputfile/'+dataset+'_nodelabel'
    queryfile=path+dataset+'_Query_wall.txt'
    outfile=path+algo+dataset+'_Query_wall_cstGrd_k'+str(k)+'_res.txt'
    queryVertexes=[] ##包含所有的查询节点
    queryAtts=[] ###包含所有的查询属性

    fq=open(queryfile,'r')
    lineCount=0
    for line in fq.readlines():
        lineCount+=1
        line=line.strip("\n") #把末尾换行符去掉
        words=line.split('\t')

        nodeStartid=words.index('node:')  ####查询节点开始的位置
        attrsStartid=words.index('attrs:') ####查询属性开始的位置

        tmp=words[nodeStartid+1:attrsStartid]
        if(len(tmp)==0):  #####可能会出现查询节点为空
            break
        nodeList=[]
        for val in tmp:
            if val:
                nodeList.append(int(val))
        queryVertexes.append(nodeList)

        attrList=words[attrsStartid+1:] ###选择所以关键词
        attrList[-1].strip('\n')  ##去不掉最后一个换行符。。
        queryAtts.append(attrList)

    fq.close()


    print 'Reading graph...'
    G=dataReader3(edgefile,labelfile)

    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root=shellIndex.root
    # #打印树
    # print 'Index Tree:'
    # displayTree(root,0)


    wf=open(outfile,'w')
    for i in range(lineCount):
        print '**************************************************************************'
        print 'NO.'+str(i)+' querying...'
        qnode=queryVertexes[i]
        qattr=queryAtts[i]
        print 'retrieveCST,k=',str(k),'...'
        H =retrieveCST(qnode,shellIndex,k)
        print 'cst:',H.nodes()
        Hi=greedyDec(H,k,qnode,qattr)
        print 'final res:',Hi.nodes()
        ####文件输出
        string=''
        for node in Hi.nodes():
            string+=str(node)+' ' ####空格分割
        wf.write(string+'\n')
        print '**************************************************************************'
    wf.close()


def testcsmStInc():
    ###############################################################################
    ####      读query文件，并将结果输出（注意结果文件与query文件相对应）###########
    ###############################################################################
    path='Data/'
    dataset='delicious'
    algo='csmSTTree/'
    edgefile=path+dataset+'_graph'
    labelfile=path+dataset+'_nodelabel'
    queryVertexes=[1,2,3] ##包含所有的查询节点
    queryAtts=['2','51'] ###包含所有的查询属性

    print 'Reading graph...'
    G=dataReader3(edgefile,labelfile)

    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root=shellIndex.root
    # #打印树
    # print 'Index Tree:'
    # displayTree(root,0)
    print  'querying...'
    qnode=queryVertexes
    qattr=queryAtts
    print 'retrieveCSM...'
    resTNodes,H,maxCoreness =retrieveCSM(qnode,shellIndex)
    print 'csmNodes:',H.nodes()
    print 'csmEdges:',H.edges()
    print 'maxCoreness:',maxCoreness
    Hi=csmSTTree(H,maxCoreness,qnode,qattr,0.5)  ####最后一个参数是结构和属性的权衡分数
    print 'final res:',Hi.nodes()

def runcsmGrD2():
    ###############################################################################
    ####      读query文件，并将结果输出（注意结果文件与query文件相对应）###########
    ###############################################################################
    path='L:/ACQData/groundTruthData/'
    data='cora'
    dataset=data+'/'+data
    algo='csmSTTree'
    edgefile=path+dataset+'_graph'
    labelfile=path+dataset+'_nodelabel'
    queryfile=path+dataset+'_query_w2'
    outfile='L:/ACQData/'+algo+'/'+data+'_query_w2_'+algo+'_res.txt'
    queryVertexes=[] ##包含所有的查询节点
    queryAtts=[] ###包含所有的查询属性
    fq=open(queryfile,'r')
    lineCount=0
    for line in fq.readlines():
        lineCount+=1
        line=line.strip("\n") #把末尾换行符去掉
        words=line.split('\t')

        nodeStartid=words.index('node:')  ####查询节点开始的位置
        attrsStartid=words.index('attr:') ####查询属性开始的位置

        tmp=words[nodeStartid+1:attrsStartid]
        if(len(tmp)==0):  #####可能会出现查询节点为空
            break
        nodeList=[]
        for val in tmp:
            if val:
                nodeList.append(int(val))
        queryVertexes.append(nodeList)

        attrList=words[attrsStartid+1:] ###选择所以关键词
        attrList[-1].strip('\n')  ##去不掉最后一个换行符。。
        queryAtts.append(attrList)
    fq.close()

    print 'Reading graph...'
    G=dataReader3(edgefile,labelfile)
    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root=shellIndex.root
    # #打印树
    # print 'Index Tree:'
    # displayTree(root,0)
    wf=open(outfile,'w')
    for i in range(lineCount):
        print '**************************************************************************'
        print 'NO.'+str(i)+' querying...'
        qnode=queryVertexes[i]
        qattr=queryAtts[i]
        print 'retrieveCSM...'
        resTNodes,H,maxCoreness =retrieveCSM(qnode,shellIndex)
        print 'csm:',H.nodes()
        print 'maxCoreness:',maxCoreness
        # Hi=greedyDec(H,maxCoreness,qnode,qattr)
        Hi=csmSTTree(H,maxCoreness,qnode,qattr,0.5)
        print 'final res:',Hi.nodes()
        ####文件输出
        string=''
        for node in Hi.nodes():
            string+=str(node)+' ' ####空格分割
        wf.write(string+'\n')
        print '**************************************************************************'
    wf.close()

if __name__=="__main__":
    runcsmGrD2()