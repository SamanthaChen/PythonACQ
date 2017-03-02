# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:OnlineProcessing.py
@time:2017/2/2611:12
@在线查询的方法类,
"""
import networkx as nx
import copy
from ShellStructIndex import ShellStructIndex as ShellIndex
from collections import defaultdict
import matplotlib.pyplot as plt

def dataReader(graphFile,nodeFile):
    '根据图文件（邻接链表格式）和节点文件（节点-别名-属性）读取图'
    G=nx.read_adjlist(graphFile,nodetype=int) #从邻接表读取图数据
    #读取节点的属性文件
    f=open(nodeFile)
    for line in f.readlines():
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
            tmp=[val for val in nattr if val in queryAttributes]  #计算节点属性与查询属性的交集
            score=sum([2.0*VwList[val]-1 for val in tmp])
            nodeAtteSocreDict[n]=score
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
            nattr=G.node[v]['attr']
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
        for attr in G.node[id]['attr']:
                if attr in queryAttrs:
                    attrNodeDict[attr].append(id)
    return attrNodeDict




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
        words=line.split() ##第一个是id，后面跟着的都是属性
        id=int(words[0])
        attr=words[1]
        if G.has_node(id):
            if G.node[id].has_key('attr'):
                G.node[id]['attr'].append(attr)
            else:
                G.node[id]['attr']=[] #新加一个列表
    return G

def selectQuery(G):
    '筛选查询节点和查询属性'
    '1. 先选一个最大的连通分量'
    Gc=max(nx.connected_component_subgraphs(G),key=len)
    '2. 计算这个连通分量的k-core分解'
    coreIndex=nx.core_number(Gc)
    '3. 将节点按照core值分组'
     #将节点按照core number进行分组
    Vk=defaultdict(list) #字典的value是列表
    sortedVk={}
    for key in sorted(Vk.keys(),reverse=True):#Vk按照core值从大到小排序
        sortedVk[key]=Vk[key]





if __name__=="__main__":
    #################      TEST 1     ###############################
    # graphFile='Data/toy-graph'
    # nodeFile='Data/toy-node'
    # G=dataReader(graphFile,nodeFile)
    # print 'ok'
    # shellIndex = ShellIndex(G)
    # shellIndex.build()
    # root=shellIndex.root
    # #打印树
    # # displayTree(root,0)
    # queryVertexes=[1,3]
    # resTNodes,H,maxCoreness =retrieveCSM(queryVertexes,shellIndex)
    # print 'csm:',H.nodes()
    # print 'maxCoreness:',maxCoreness
    # ###假设没有指定查询属性，取查询节点属性的交集
    # queryAttributes=['tree','algorithm']
    # H1=greedyDec(H,3,queryVertexes,queryAttributes)
    # print 'final res:',H1.nodes()

    ####################   TEST 2   ##############################
    edgefile='Data/delicious_alledges.dat'
    labelfile='Data/user_tag2.dat'
    G=dataReader2(edgefile,labelfile)
    print 'ok'
    nx.draw(G,node_size = 30,with_labels=True)
    plt.show()

