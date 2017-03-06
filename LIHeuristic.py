# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:LIHeuristic.py
@time:2017/3/616:24
@Fuction 为了O(1)时间取得li分数
"""
import networkx as nx
from collections import defaultdict
class LIHeuristic:
    '计算连接分数的类'
    def __init__(self,G,curGraph,queryAttrs,alpha):
        self.G=G
        self.queryAttrs=queryAttrs
        self.alpha=alpha
        ###当前最大链接分数
        self.maxaScore=0
        self.maxcScore=0
        #####当前节点的连接数分组
        self.connectedScore={} ###这个分数没有归一化
        self.attributeScore={} ###这个分数没有归一化
        self.totalScore={}     ###这个分数归一化了
        self.VwList={}
        ####按连接分数分的小组
        # self.groupOfNodes=[None]*(nx.number_of_nodes(G))
        ####节点到组号的映射
        self.nodeGroup=defaultdict(list)
        '1:计算当前每个节点的连接数和组号'
        resVertexs=curGraph.nodes()
        for u in resVertexs:
            for nei in G.neighbors(u):
                if nei not in resVertexs:
                    if not self.nodeGroup.has_key(nei):
                        self.nodeGroup[nei]=1 #一开始连接了一个
                    else:
                        self.nodeGroup[nei]+=1

        '2:更新连接分数分组，当前最大连接分数'
        for node,index in self.nodeGroup.items():
            # self.groupOfNodes[index].append(node)
            if index>self.maxcScore:
                self.maxcScore=index

        '3:计算VkList'
        self.VwList=self.VwList.fromkeys(queryAttrs,0)
        for qa in queryAttrs:
            for node in resVertexs:
                if G.node[node].has_key('attr') and G.node[node]['attr']!=None:
                    for na in G.node[node]['attr']:
                        if na==qa:
                            self.VwList[qa]+=1
        '4:计算当前候选节点的属性得分'
        curNodes=self.nodeGroup.keys()
        self.connectedScore=self.connectedScore.fromkeys(curNodes,0.0)
        self.attributeScore=self.attributeScore.fromkeys(curNodes,0.0)
        self.totalScore=self.totalScore.fromkeys(curNodes,0.0)
        for n in curNodes:
            ####计算连接分数
            self.connectedScore[n]=self.nodeGroup[n] #连接个数
            # if self.connectedScore[n]>self.maxcScore:
            #     maxcScore=self.connectedScore[n]
            #####计算属性得分
            if self.G.node[n].has_key('attr') and self.G.node[n]['attr']!=None:
                for a in self.G.node[n]['attr']:
                    if a in queryAttrs:
                        self.attributeScore[n]+=2*self.VwList[a]-1
            #####更新最大属性分数
            if self.attributeScore[n]>self.maxaScore:
                self.maxaScore=self.attributeScore[n]
        '5:最后利用最大分数，归一化计算总分数'
        for n in curNodes:
            tmp=alpha * (float(self.connectedScore[n])/float(self.maxcScore))+(1-alpha) * (float(self.attributeScore[n])/float(self.maxaScore))
            self.totalScore[n]=tmp



    def addNode(self,node,linkG):
        '往graph添加节点node后，更新分数'
        neighbors=self.G.neighbors(node)
        numberofNei=0
        nodes=linkG.nodes()
        ####遍历小的比较省时间
        if(len(nodes)<len(neighbors)):
            for n in nodes:
                if n in neighbors:
                    numberofNei+=1
        else:
            for n in neighbors:
                if n in nodes:
                    numberofNei+=1
        '1.更新分组,更新连通分数'
        self.groupOfNodes[numberofNei].append(node)
        self.nodeGroup[node]=numberofNei
        self.connectedScore=numberofNei
        if numberofNei>self.maxcScore:
            self.maxcScore=numberofNei
        '2.不更新VkList，计算自己的属性得分'
        aScore=0.0
        for qa in self.queryAttrs:
            if self.G.node[node].has_key('attr') and self.G.node[node]['attr']!=None:
                for na in self.G.node[node]['attr']:
                    if na==qa:
                        aScore+=2*self.VwList[qa]-1
        if aScore>self.maxaScore:
            self.maxaScore=aScore
        '3.更新总分（因为每一次最大分数都会变）(删除时候不更新，反正保持最大就行)'
        for n in self.nodeGroup.keys():
            tmp=self.alpha * (float(self.connectedScore[n])/float(self.maxcScore))+(1-self.alpha) * (float(self.attributeScore[n])/float(self.maxaScore))
            self.totalScore[n]=tmp

    def getBestNode(self):
        '获得当前分数最大的节点'

        if len(self.totalScore)==0:
            return -1
        else:
            maxItem=max(self.totalScore.items(),key=lambda x:x[1])
            node=maxItem[0]
            score=maxItem[1]
            '1.从待访问集合中删除'
            # self.groupOfNodes[self.connectedScore[node]].remove(node)
            del self.nodeGroup[node]
            del self.connectedScore[node]
            del self.attributeScore[node]
            del self.totalScore[node]
            '2.node加入solution之后，需要更新node邻居的连接数'
            neighbors=self.G.neighbors(node)
            for nei in neighbors:
                if self.nodeGroup.has_key(nei):
                    oldGroup=self.nodeGroup[nei]
                    # self.groupOfNodes[oldGroup].remove(nei)
                    newGroup=oldGroup+1
                    self.nodeGroup[nei]=newGroup
                    if newGroup>self.maxcScore:
                        self.maxcScore=newGroup
                    # self.groupOfNodes[newGroup].append(nei)
            '3.node加入solution后，VwList需要更新'
            '更新VkList，更新最大属性分数'
            for qa in self.queryAttrs:
                if self.G.node[node].has_key('attr') and self.G.node[node]['attr']!=None:
                    for na in self.G.node[node]['attr']:
                        if na==qa:
                            self.VwList[qa]+=1  ###node与查询节点重合的属性出现频率需要+1
            '4.更新属性得分'
            curNodes=self.nodeGroup.keys()
            for n in curNodes:
                #####计算属性得分
                if self.G.node[n].has_key('attr') and self.G.node[n]['attr']!=None:
                    for a in self.G.node[n]['attr']:
                        if a in self.queryAttrs:
                            self.attributeScore[n]+=2*self.VwList[a]-1
                #####更新最大属性分数
                if self.attributeScore[n]>self.maxaScore:
                    self.maxaScore=self.attributeScore[n]
            '5.更新总分（因为每一次最大分数都会变）(删除时候不更新，反正保持最大就行)'
            for n in self.nodeGroup.keys():
                tmp=self.alpha * (float(self.connectedScore[n])/float(self.maxcScore))+(1-self.alpha) * (float(self.attributeScore[n])/float(self.maxaScore))
                self.totalScore[n]=tmp
            return node



