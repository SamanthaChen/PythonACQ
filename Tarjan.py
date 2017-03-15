# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:Tarjan.py
@time:2017/2/2319:13
@function: tarjan实现的查找最低公共祖先算法
"""
from TNode import  TNode
from UNode import UNode
# from UnionFind import UnionFind

class Query:
    def __init__(self,p1,p2):
        self.p1=p1
        self.p2=p2
        self.lca=None

def makeSet(p):
    p.parent=p

def find(p):
    r=p
    while(r.parent!=r):
        r=r.parent
    return r

def union(p,q):
    q.parent=p


def LCA(p,queryList,checked,ufList):
    makeSet(ufList[p.data])
    # uf.find(ufList[p.data]).parent=ufList[p.data] #将自己的祖先
    for node in p.childList:
        LCA(node,queryList,checked,ufList)
        union(ufList[p.data],ufList[node.data])
        find(ufList[p.data]).parent=ufList[p.data]  #这条栈溢出？
    checked[p.data]=True
    for query in queryList:
        if query.p1==p:
            if checked[query.p2.data]==True:
                query.lca=find(ufList[query.p2.data]).value
        elif query.p2==p:
             if checked[query.p1.data]==True:
                query.lca=find(ufList[query.p1.data]).value
        else:
            continue

def displayTree(root,level):
    '打印树'
    string=""
    if root:
        #前置的空格
        preStr=""
        for i in range(level):
            preStr=preStr+"     "
        string=string+preStr+"----"+str(root.data)

        print string

        #打印孩子节点
        if root.childList:
            for chid in root.childList:
                displayTree(chid,level+1)

'测试这个算法'
if __name__=="__main__":
    nodeList=[]
    for i in range(0,13):
        nodeList.append(TNode(data=i))
    nodeList[0].childList.append(nodeList[1])
    nodeList[1].childList.append(nodeList[2])
    nodeList[1].childList.append(nodeList[3])
    nodeList[2].childList.append(nodeList[4])
    nodeList[2].childList.append(nodeList[5])
    nodeList[3].childList.append(nodeList[6])
    nodeList[3].childList.append(nodeList[7])
    nodeList[5].childList.append(nodeList[8])
    nodeList[5].childList.append(nodeList[9])
    nodeList[7].childList.append(nodeList[10])
    nodeList[7].childList.append(nodeList[11])
    nodeList[7].childList.append(nodeList[12])

    #打印树
    displayTree(nodeList[0],0)

    queryList=[] #存的是树结构啊
    queryList.append(Query(nodeList[8],nodeList[6]))
    queryList.append(Query(nodeList[2],nodeList[8]))
    queryList.append(Query(nodeList[6],nodeList[12]))

    checked=[] #需要一个数组存储访问过的节点
    for i in range(0,13):
        checked.append(False)
    ufList=[] #这个数据结构存储UNode的数据结构
    for i in range(0,13):
        unode=UNode(nodeList[i].data)
        ufList.append(unode)


    #lca查询过程
    LCA(nodeList[0],queryList,checked,ufList,)

    #打印结果
    for q in queryList:
        print 'p1:',q.p1.data,' p2:',q.p2.data,' lca:',q.lca
