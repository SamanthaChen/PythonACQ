# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:LCA_Tarjar.py
@time:2017/2/2316:32
"""
from TNode import TNode
class lcaAns:
    def __init__(self,u,v):
        self.u=u
        self.v=v
        self.lca=None

    def __str__(self):
        return "u:"+str(self.u)+" v:"+str(self.v)+" lca:"+self.lca

def tarjan(u,lcaInfo,finalAns):

    checked[u]=True;
    for chilNode in u.chidList:
        tarjan(chilNode,lcaInfo,finalAns)
        union(u,chilNode)
        checked[chilNode]=True
    for v in lcaInfo[u]:
        if(checked[v]==True):
            pair = lcaAns(u,v)
            pair.lca=find(v)
            finalAns.append(pair)





    #查询的算法
if __name__=='__main__':


    a=TNode(data='A')
    b=TNode(data='B')
    c=TNode(data='C')
    d=TNode(data='D')
    e=TNode(data='E')
    f=TNode(data='F')
    g=TNode(data='G')
    h=TNode(data='H')
    i=TNode(data='I')
    j=TNode(data='J')
    a.chidList.append(b)
    a.chidList.append(c)
    b.chidList.append(d)
    b.chidList.append(e)
    d.chidList.append(f)
    d.chidList.append(g)
    e.chidList.append(h)
    e.chidList.append(i)
    e.chidList.append(j)


    checked={};
    checked[a]=False
    checked[b]=False
    checked[c]=False
    checked[d]=False
    checked[e]=False
    checked[f]=False
    checked[g]=False
    checked[h]=False
    checked[i]=False
    checked[j]=False

    lcaInfo = {a:[b,c,j],f:[h,b,c]}
    finalAns=[]
    for q in lcaInfo.keys():
        tarjan(q,lcaInfo,finalAns)
    for ans in finalAns:
        print ans










'包含所有并查集方法的类'
def makeSet(self,x): #这个x必须是UNode结构吗
    x.parent=x
    x.rank=0
    x.represent=x.value

def find(self,x):
    if(x.parent!=x):
         x.parent=self.find(x.parent)
    return x.parent

def union(self,x,y):
    xRoot=self.find(x)
    yRoot=self.find(y)
    if(xRoot==yRoot): return

    if(xRoot.rank<yRoot.rank):
        xRoot.parent=yRoot
    elif(xRoot.rank>yRoot.rank):
        yRoot.parent=xRoot
    else:
        yRoot.parent=xRoot
        xRoot.rank=xRoot.rank+1