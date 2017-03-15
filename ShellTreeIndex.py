# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:ShellTreeIndex.py
@time:2017/2/2017:12
"""

import networkx as nx
import matplotlib.pyplot as plt
from UnionFind import UnionFind
from UNode import UNode
from collections import defaultdict

from TNode import TNode
import copy

def dataReader(graphFile,nodeFile):
    G=nx.read_adjlist(graphFile,nodetype=int) #从邻接表读取图数据
    #读取节点的属性文件
    f=open(nodeFile)
    for line in f.readlines():
        words = line.split()
        G.node[int(words[0])]['name']=words[1] #读取节点的name
        G.node[int(words[0])]['attr']=words[2:] #读取节点的属性
    return G

def build(G):
    '采用并查集自底向上建立TreeIndex'
    N=nx.number_of_nodes(G) #图的节点个数
    '步骤1：计算k-core，按coreness分组'
    coreDict=nx.core_number(G)
    #将节点按照core number进行分组
    Vk=defaultdict(list) #字典的value是列表
    for key,value in coreDict.iteritems():
        Vk[value].append(key)
    #将Vk按照coreness(key)进行排序，降序
    # sortedVk=sorted(Vk.items(),key=lambda d:d[0],reverse=True)
    '步骤2：初始化并查集和一些需要的数据结构'
    unodeArr =[] #存储的是并查集的节点
    uf = UnionFind() #包含所有并查集方法的类
    restNodeList=[] #储存没有父母的节点，最后直接连接到core为0的根节点下方作为孩子
    vertexTNodelist=[None]*N #图节点到TNode的映射的列表
    core0List=[] #coreness=0的节点，作为这棵树的根
    for i in range(N):
        unode=UNode(i)
        uf.makeSet(unode)
        unodeArr.append(unode)
    '步骤3：自底向上建立树'
    #level by level,
    for key in sorted(Vk.keys(),reverse=True):
        curcore=key
        vkList=Vk[key]
        if curcore>0:
            idUFMap={}#(id->UNode)这里用字典但是unodeArr用列表是因为这里的id不一定是连续的
            '步骤3.1： 先在同一个core值节点中找连通分量，利用一个临时并查集idUFMap'
            for id in vkList:
                if not idUFMap.has_key(id):#加入Vk
                    unode=UNode(id)
                    uf.makeSet(unode)
                    idUFMap[id]=unode
                for ngid in G.neighbors(id):
                    if coreDict[ngid]>=coreDict[id]:#先处理core大的
                        if coreDict[ngid]>coreDict[id]:
                            ngid=uf.find(unodeArr[ngid]).value #如果邻居的core比较大，说明已经处理过，用父母代替
                        if not idUFMap.has_key(ngid):#加入V'
                            unode=UNode(ngid)
                            uf.makeSet(unode)
                            idUFMap[ngid]=unode
                        uf.union(idUFMap[id],idUFMap[ngid])
            '步骤3.2：按照上面临时并查集的结果，给图节点分组，找树节点孩子'
            ufGNodeMap=defaultdict(list) #(UNode->[vertex])unode到同一个组的unode的图节点的字典
            ufTNodeMap=defaultdict(list) #(UNode->[TNode])unode到TNode的映射
            for reId,reUNode in idUFMap.iteritems():
                newParent=uf.find(reUNode) #在新的并查集里面，节点的父母
                if coreDict[reId]==curcore:#同一个core值的节点分成一组
                    ufGNodeMap[newParent].append(reId)
                if coreDict[reId]>curcore:#由于是自底向上的，当前这个reid应该已经处理过了
                    oldParent=unodeArr[reId] #这个是外面的并查集记录的reId的父母
                    tnode=vertexTNodelist[oldParent.represent]
                    ufTNodeMap[newParent].append(tnode)
            '步骤3.3：产生新的TNode节点并建立树节点之间的联系'
            for parent,nodeList in ufGNodeMap.iteritems():
                childList=ufTNodeMap[parent]
                tnode=TNode(curcore) #新建一个树节点
                tnode.nodeList=nodeList
                if childList:#如果孩子不为空，给树节点添加孩子节点
                    tnode.childList=childList #这里用不用深拷贝？
                restNodeList.append(tnode) #假设这个节点目前没有父母咯
                #更新(id->TNode)
                for nodeId in nodeList:
                    vertexTNodelist[nodeId]=tnode
                #更新没有父母的树节点列表
                for subTNode in tnode.childList:
                    restNodeList.remove(subTNode)
            '步骤3.4： 更新外面的并查集'
            for id in vkList:
                x=unodeArr[id] #当前节点的UNode
                for ngid in G.neighbors(id):
                    if coreDict[ngid]>=curcore:#遍历边的优先级，core大的先检查，保证自底向上的
                        y=unodeArr[ngid]
                        uf.union(x,y)
                #更新represent节点
                xRoot=uf.find(x)
                xRepresent=uf.find(x).represent
                if coreDict[xRepresent]>coreDict[id]:
                    xRoot.represent=id
        else:#core为0的节点作为根
            core0List=vkList

    '步骤4：建立root节点'
    root = TNode(0)
    root.nodeList=core0List
    root.childList=copy.deepcopy(restNodeList)
    '步骤5：在树节点上获得nodeList的属性的倒排'
    attachKw(root,G)
    return root,vertexTNodelist,coreDict

def attachKw(root,G):
    'BFS遍历树的所有节点并生成关键词倒排'
    kwMap=defaultdict(list)
    '步骤1：先生成root节点的倒排属性'
    nodeList=root.nodeList
    if nodeList:
        for id in nodeList:
            for attr in  G.node[id]['attr']:
                kwMap[attr].append(id)
    root.kwMap=copy.deepcopy(kwMap)
    '步骤2：迭代生成孩子节点的倒排属性'
    for chidTNode in root.childList:
        attachKw(chidTNode,G)


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



def retrieveCSM(queryVertexes,root,vertexTNodeList,coreDict):
    '自底向上，一层层往上找，最终的查询节点会汇聚到一个最低的公共祖先'
    '步骤1：计算查询节点集合中最大的coreness'
    maxQCore = 0
    queryTNodeSet=set() #集合类型，包含查询节点所在的树集合
    for query in queryVertexes:
        if coreDict[query]>maxQCore:
            maxQCore=coreDict[query]
        queryTNodeSet.add(vertexTNodeList[query])
    '步骤2:从底层开始往上找最低公共祖先'
    csmTNodes=[] #存储的是包含查询节点的corenness最大的树节点集合
    curLevel=[]








if __name__=="__main__":

    graphFile='Data/toy-graph'
    nodeFile='Data/toy-node'
    G=dataReader(graphFile,nodeFile)
    root,vertexTNodeList,coreDict=build(G)
    #打印树
    displayTree(root,0)





    ######画图
    # pos=nx.spring_layout(G)
    # nx.draw_networkx_nodes(G, pos, alpha=0.7,vmin=0.0,vmax=1.0)
    # nx.draw_networkx_edges(G, pos,alpha=0.3)
    # nx.draw_networkx_labels(G,pos)
    # plt.axis("off")
    # plt.show()