# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:ShellStructIndex.py
@time:2017/2/2422:56
@Function:建立shell索引的一些方法
@Revise:
2017.2.26
重写自ShellTreeIndex.py文件
改写成类，TNode添加id，指向父亲的指针
"""
import networkx as nx
import matplotlib.pyplot as plt
from UnionFind import UnionFind
from UNode import UNode
from collections import defaultdict

from TNode import TNode
import copy

class ShellStructIndex:

    '属性'
     ##索引的属性
    G=nx.Graph()
    coreDict={} #图节点到core的映射
    vertexTNodelist= [] #图节点到树节点的映射，假设图节点的序号是连续的，所以用列表
    root=None

    def __init__(self,G):
        ##索引初始化需要的
        ShellStructIndex.G=G


    def build(self):
        '采用并查集自底向上建立TreeIndex'
        N=nx.number_of_nodes(ShellStructIndex.G) #图的节点个数
        '步骤1：计算k-core，按coreness分组'
        ShellStructIndex.coreDict=nx.core_number(ShellStructIndex.G)
        #将节点按照core number进行分组
        Vk=defaultdict(list) #字典的value是列表
        for key,value in ShellStructIndex.coreDict.iteritems():
            Vk[value].append(key)
        #将Vk按照coreness(key)进行排序，降序
        # sortedVk=sorted(Vk.items(),key=lambda d:d[0],reverse=True)
        '步骤2：初始化并查集和一些需要的数据结构'
        restNodeList=[] #储存没有父母的节点，最后直接连接到core为0的根节点下方作为孩子
        ShellStructIndex.vertexTNodelist=[None]*(N+1) #图节点到TNode的映射的列表
        core0List=[] #coreness=0的节点，作为这棵树的根
        #############初始化并查集#############
        unodeArr =[] #存储的是并查集的节点(id->UNode)
        uf = UnionFind() #包含所有并查集方法的类
        for i in range(N):
            unode=UNode(i)
            uf.makeSet(unode)
            unodeArr.append(unode)
        '步骤3：自底向上建立树'
        #level by level,
        tnodeCounter=0 ##计算TNode个数的计数器
        for key in sorted(Vk.keys(),reverse=True):#Vk按照core值从大到小排序
            curcore=key
            vkList=Vk[key]
            if curcore>0:
                idUFMap={}#(id->UNode)这里用字典但是unodeArr用列表是因为这里的id不一定是连续的(临时的一个并查集映射)
                '步骤3.1： 先在同一个core值节点中找连通分量，利用一个临时并查集idUFMap'
                for id in vkList:
                    if not idUFMap.has_key(id):#加入Vk
                        unode=UNode(id)
                        uf.makeSet(unode)
                        idUFMap[id]=unode
                    for ngid in ShellStructIndex.G.neighbors(id):
                        if ShellStructIndex.coreDict[ngid]>=ShellStructIndex.coreDict[id]:#先处理core大的
                            if ShellStructIndex.coreDict[ngid]>ShellStructIndex.coreDict[id]:
                                ngid=uf.find(unodeArr[ngid]).value #如果邻居的core比较大，说明已经处理过，用父母代替
                            if not idUFMap.has_key(ngid):#加入V'
                                unode=UNode(ngid)
                                uf.makeSet(unode)
                                idUFMap[ngid]=unode
                            uf.union(idUFMap[id],idUFMap[ngid]) #合并id和他的邻居（或者邻居的父母）
                '步骤3.2：按照上面临时并查集的结果，给图节点分组，找树节点孩子'
                ufGNodeMap=defaultdict(list) #(UNode->[vertex])unode到同一个组的unode的图节点的字典
                ufTNodeMap=defaultdict(list) #(UNode->[TNode])unode到TNode的映射
                for reId,reUNode in idUFMap.iteritems():
                    newParent=uf.find(reUNode) #在新的并查集里面，节点的父母
                    if ShellStructIndex.coreDict[reId]==curcore:#同一个core值的节点分成一组
                        ufGNodeMap[newParent].append(reId)
                    if ShellStructIndex.coreDict[reId]>curcore:#由于是自底向上的，当前这个reid应该已经处理过了
                        oldParent=unodeArr[reId] #这个是外面的并查集记录的reId的父母
                        tnode=ShellStructIndex.vertexTNodelist[oldParent.represent]
                        ufTNodeMap[newParent].append(tnode)
                '步骤3.3：产生新的TNode节点并建立树节点之间的联系'
                for parent,nodeList in ufGNodeMap.iteritems():
                    childList=ufTNodeMap[parent]
                    tnodeCounter=tnodeCounter+1 #
                    tnode=TNode(curcore,tnodeCounter) #新建一个树节点(给定coreness和树节点编号)（re：2017.2.26）
                    tnode.nodeList=nodeList
                    if childList:#如果孩子不为空，给树节点添加孩子节点
                        tnode.childList=childList #这里用不用深拷贝？
                        #####给孩子节点添加父母,方便后面的retrieve(re:2017.2.26)########
                        for chid in childList:
                            chid.parent=tnode
                    restNodeList.append(tnode) #假设这个节点目前没有父母咯
                    #更新(id->TNode)
                    for nodeId in nodeList:
                        ShellStructIndex.vertexTNodelist[nodeId]=tnode
                    #更新没有父母的树节点列表
                    for subTNode in tnode.childList:
                        restNodeList.remove(subTNode)
                '步骤3.4： 更新外面包含所有节点的并查集'
                for id in vkList:
                    x=unodeArr[id] #当前节点的UNode
                    for ngid in ShellStructIndex.G.neighbors(id):
                        if ShellStructIndex.coreDict[ngid]>=curcore:#遍历边的优先级，core大的先检查，保证自底向上的
                            y=unodeArr[ngid]
                            uf.union(x,y)
                    #更新represent节点
                    xRoot=uf.find(x)
                    xRepresent=uf.find(x).represent
                    if ShellStructIndex.coreDict[xRepresent]>ShellStructIndex.coreDict[id]:
                        xRoot.represent=id
            else:#core为0的节点作为根
                core0List=vkList

        '步骤4：建立root节点'
        tnodeCounter=tnodeCounter+1#(re:2017.2.26)
        ShellStructIndex.root = TNode(core=0,data=tnodeCounter)
        ShellStructIndex.root.nodeList=core0List
        ShellStructIndex.root.childList=restNodeList  #这里需要深拷贝（copy.deepcopy(restNodeList)）吗？
        ####(re:2017.2.26)
        for chid in ShellStructIndex.root.childList:
            chid.parent=ShellStructIndex.root
        #####把节点到树的映射也更新一下####
        for v in core0List:
            ShellStructIndex.vertexTNodelist[v]=ShellStructIndex.root
        '步骤5：在树节点上获得nodeList的属性的倒排'
        self.attachKw(ShellStructIndex.root)



    def attachKw(self,root):
        'BFS遍历树的所有节点并生成关键词倒排'
        kwMap=defaultdict(list)
        '步骤1：先生成root节点的倒排属性'
        nodeList=root.nodeList
        if nodeList:
            for id in nodeList:
                for attr in  ShellStructIndex.G.node[id]['attr']:
                    kwMap[attr].append(id)
        root.kwMap=copy.deepcopy(kwMap)
        '步骤2：迭代生成孩子节点的倒排属性'
        for chidTNode in root.childList:
            self.attachKw(chidTNode)

    def displayTree(self,root,level):
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
                   self. displayTree(chid,level+1)