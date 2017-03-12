# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:CoreStuctIndex.py
@time:2017/3/220:12
"""
import networkx as nx
import copy
from ShellStructIndex import ShellStructIndex as ShellIndex
from collections import defaultdict
import matplotlib.pyplot as plt




def build(G):
    '建立coreIndex'
    '0:需要的一些数据结构'
    nodeGroup={} ##节点<-->分组id
    groupsOfNodes=defaultdict(list)###分组的连通分量
    coreComposition={}
    coreConnectedComponents={}
    '1:k-core分解'
    coreIndex=nx.core_number(G)
    '2:将节点按照core number进行分组'
    coreGroup=defaultdict(list) #字典的value是列表
    for key,value in coreIndex.iteritems():
        coreGroup[value].append(key)
    '3:自底向上'
    for key in sorted(coreGroup.keys(),reverse=True):#Vk按照core值从大到小排序
        curCoreness=key
        vkList=coreGroup[curCoreness] #该core值下的节点列表
        for id in vkList:
            ##遍历所有邻居
            for neiId in G.neighbors(id):
                ###假设邻居已经分组,将id的分组设为与neiId相同
                if( not nodeGroup.has_key(id)) and (nodeGroup.has_key(neiId)):
                    groupid=nodeGroup[neiId]
                    nodeGroup[id]=groupid
                    ###下面这个操作的前提是groupid已经有了
                    groupsOfNodes[groupid].append(id)
                elif(nodeGroup.has_key(id) and nodeGroup.has_key(neiId) and nodeGroup[id]!=nodeGroup[neiId]):
                    ####假设id和neiId都已经有分组了，但是分组都不一样，需要进行合并
                    idGroup=nodeGroup[id]
                    neiIdGroup=nodeGroup[neiId]
                    if(len(groupsOfNodes[idGroup])<len(groupsOfNodes[neiId])):
                        for oldNode in groupsOfNodes(idGroup):
                            nodeGroup[oldNode]=neiIdGroup
                            groupsOfNodes[neiId].append(oldNode)
                        ##删除小的那个分组
                        del groupsOfNodes[idGroup]
                    else:
                        for oldNode in groupsOfNodes(neiIdGroup):
                            nodeGroup[oldNode]=idGroup
                            groupsOfNodes[idGroup].append(oldNode)
                        ###删除小的
                            del groupsOfNodes[neiId]
            ###假如没有邻居
            if(not nodeGroup.has_key(id)):
                groupsOfNodes[id].append(id)
                nodeGroup[id]=id
        #####将节点进行分组












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

if __name__=="__main__":
    edgefile='Data/delicious_alledges.dat'
    labelfile='Data/user_tag2.dat'
    G=dataReader2(edgefile,labelfile)
    print 'ok'
    nx.draw(G,node_size = 30,with_labels=True)
    plt.show()