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
        '初始化的时候就已经计算好了当前候选节点得分。G是即候选范围，curGraph是最小连通的图（已经加入结果集中）'
        self.G=G ##总的图
        self.queryAttrs=queryAttrs
        self.alpha=alpha
        ###当前最大链接分数
        self.maxaScore=0 ##最大属性分数
        self.maxcScore=0 ##最大结构分数
        #####当前节点的连接数分组
        self.connectedScore={} ###这个分数没有归一化
        self.attributeScore={} ###这个分数没有归一化
        self.totalScore={}     ###这个分数归一化了
        self.VwList={} ###结果集中属性出现频率字典
        self.queryAttrGroup=defaultdict(list) ##候选集中属性分组
        ####按连接分数分的小组
        # self.groupOfNodes=[None]*(nx.number_of_nodes(G))
        ####映射个数
        # self.nodeGroup=defaultdict(list) ###这个类已经多余了，跟connectedScore一样
        '1:计算当前每个节点的连接数和组号'
        resVertexs=curGraph.nodes()
        for u in resVertexs:
            for nei in G.neighbors(u):
                if nei not in resVertexs:
                    if not self.connectedScore.has_key(nei):
                        self.connectedScore[nei]=1 #一开始连接了一个
                    else:
                        self.connectedScore[nei]+=1

        '2:更新连接分数分组，当前最大连接分数'
        # for node,index in self.nodeGroup.items():
        #     # self.groupOfNodes[index].append(node)
        #     if index>self.maxcScore:
        #         self.maxcScore=index

        '3:计算VkList'
        self.VwList=self.VwList.fromkeys(queryAttrs,0)  #初始化是0分
        for qa in queryAttrs:
            for node in resVertexs:
                if G.node[node].has_key('attr') and G.node[node]['attr']!=None:
                    for na in G.node[node]['attr']:
                        if na==qa:
                            self.VwList[qa]+=1
        '4:计算当前候选节点的属性得分'
        curNodes=self.connectedScore.keys() ###当前候选节点
        self.connectedScore=self.connectedScore.fromkeys(curNodes,0.0) #连接分数
        self.attributeScore=self.attributeScore.fromkeys(curNodes,0.0) #属性分数
        self.totalScore=self.totalScore.fromkeys(curNodes,0.0) #总分
        for n in curNodes:
            '2:更新连接分数分组，当前最大连接分数'
            if self.connectedScore[n]>self.maxcScore:
                self.maxcScore=self.connectedScore[n]
            #####计算属性得分
            if self.G.node[n].has_key('attr') and self.G.node[n]['attr']!=None:
                for a in queryAttrs: ###小的筛能快一下吧
                    if a in self.G.node[n]['attr']:
                        self.attributeScore[n]+=2*self.VwList[a]-1
                        self.queryAttrGroup[a].append(n) ###候选节点的属性分组
            #####更新最大属性分数
            if self.attributeScore[n]>self.maxaScore:
                self.maxaScore=self.attributeScore[n]
        '5:最后利用最大分数，归一化计算总分数'
        for n in curNodes:
            tmp=0
            if self.maxaScore!=0 and self.maxcScore!=0:
                tmp=alpha * (float(self.connectedScore[n])/float(self.maxcScore))+(1-alpha) * (float(self.attributeScore[n])/float(self.maxaScore))
            elif self.maxcScore !=0:
                tmp = alpha * (float(self.connectedScore[n]) / float(self.maxcScore))
            elif self.maxaScore!=0:
                tmp=(1-alpha) * (float(self.attributeScore[n])/float(self.maxaScore))
            self.totalScore[n]=tmp



    def addNode(self,node,solutionNodes):
        '添加候选节点node，更新分数'
        neighbors=self.G.neighbors(node)
        numberofNei=0
        nodes=solutionNodes
        ####遍历小的比较省时间
        if(len(nodes)<len(neighbors)): ####’计算在结果集中的邻居个数‘
            for n in nodes:
                if n in neighbors:
                    numberofNei+=1
        else:
            for n in neighbors:
                if n in nodes:
                    numberofNei+=1
        '1.更新分组,更新连通分数'
        # self.groupOfNodes[numberofNei].append(node)
        self.nodeGroup[node]=numberofNei
        self.connectedScore[node]=numberofNei
        if numberofNei>self.maxcScore:
            self.maxcScore=numberofNei
        '2.不更新VkList（因为还没加到结果集中），计算自己的属性得分'
        aScore=0.0
        for qa in self.queryAttrs:
            if self.G.node[node].has_key('attr') and self.G.node[node]['attr']!=None:
                if qa in self.G.node[node]['attr']:
                    aScore+=2*self.VwList[qa]-1
                    self.queryAttrGroup[qa].append(node)  ###加到候选属性集分组
        if aScore>self.maxaScore:
            self.maxaScore=aScore
        self.attributeScore[node]=aScore # '计算自己属性得分'

        '3.更新总分（因为每一次最大分数都会变）(删除时候不更新，反正保持最大就行)'
        for n in self.nodeGroup.keys():
            tmp=0
            if self.maxcScore!=0 and self.maxaScore!=0:
                tmp=self.alpha * (float(self.connectedScore[n])/float(self.maxcScore))+(1-self.alpha) * (float(self.attributeScore[n])/float(self.maxaScore))
            elif self.maxcScore !=0:
                tmp = self.alpha * (float(self.connectedScore[n]) / float(self.maxcScore))
            elif self.maxaScore!=0:
                tmp=(1-self.alpha) * (float(self.attributeScore[n])/float(self.maxaScore))
            self.totalScore[n]=tmp

    def addNodeList(self, nodeList, solutionNodes):
        '批量添加候选节点列表nodeList，更新分数'
        '1.更新连通分数'
        for node in nodeList:
            for seed in solutionNodes:
                if self.G.has_edge(node,seed):
                    if self.connectedScore.has_key(node):
                        self.connectedScore[node]+=1
                    else:
                        self.connectedScore[node]=1
                else:
                    self.connectedScore[node]=0
            '更新最大分数'
            if self.connectedScore[node]>self.maxcScore:
                self.maxcScore=self.connectedScore[node]


        '2.不更新VkList（因为还没加到结果集中），计算自己的属性得分'

        for node in nodeList:
            aScore = 0.0
            if self.G.node[node].has_key('attr') and self.G.node[node]['attr'] != None:
                for qa in self.queryAttrs:
                    '###只有节点包含属性才可以'
                    if qa in self.G.node[node]['attr']:
                        aScore += 2 * self.VwList[qa] - 1
                        '属性节点分组'
                        self.queryAttrGroup[qa].append(node)  ###加到候选属性集分组
                        if aScore > self.maxaScore:
                            self.maxaScore = aScore
            '##其他情况一律为0'
            self.attributeScore[node]=aScore


        '3.更新总分（因为每一次最大分数都会变）(删除时候不更新，反正保持最大就行)'
        for n in self.connectedScore.keys():
            tmp = 0.0
            if self.maxcScore != 0 and self.maxaScore != 0:
                tmp = self.alpha * (float(self.connectedScore[n]) / float(self.maxcScore)) + (1 - self.alpha) * (
                float(self.attributeScore[n]) / float(self.maxaScore))
            elif self.maxcScore != 0:
                tmp = self.alpha * (float(self.connectedScore[n]) / float(self.maxcScore))
            elif self.maxaScore != 0:
                tmp = (1 - self.alpha) * (float(self.attributeScore[n]) / float(self.maxaScore))
            self.totalScore[n] = tmp

    def getBestNode(self):
        '获得当前分数最大的节点'
        '2017.3.30改，删去nodegroup'
        if len(self.totalScore)==0:
            return -1 ###已经没有候选节点了，返回-1
        else:
            maxItem=max(self.totalScore.items(),key=lambda x:x[1]) ##最大的选项
            node=maxItem[0]
            # score=maxItem[1]
            '1.从待访问集合中删除'
            # self.groupOfNodes[self.connectedScore[node]].remove(node)
            # del self.nodeGroup[node]
            del self.connectedScore[node]
            del self.attributeScore[node]
            del self.totalScore[node]
            '从候选属性集分组中删除'
            for qa in self.queryAttrs:
                if self.G.node[node].has_key('attr') and self.G.node[node]['attr'] != None:
                    if qa in self.G.node[node]['attr']:
                        self.queryAttrGroup[qa].remove(node)
            '2.node加入solution之后，需要更新node邻居（在候选集中）的连接数'
            neighbors=self.G.neighbors(node)
            for nei in neighbors:
                if self.connectedScore.has_key(nei):
                    self.connectedScore[nei]+=1
                    if self.connectedScore[nei] > self.maxcScore:
                        self.maxcScore = self.connectedScore[nei]

            '3.node加入solution后，VwList需要更新,受影响属性分组下的节点的属性分数也要更新'
            '更新VkList，更新最大属性分数'
            for qa in self.queryAttrs:
                if self.G.node[node].has_key('attr') and self.G.node[node]['attr']!=None:
                    if qa in self.G.node[node]['attr']: ##qa是受影响的查询属性
                            self.VwList[qa]+=1  ###node与查询节点重合的属性出现频率需要
                            #####node于qa交集的属性下的分组的属性分数需要更新，其他节点不受影响
                            for nn in self.queryAttrGroup[qa]:
                                # print 'group:',self.queryAttrGroup[qa]
                                # print 'as:',self.attributeScore.keys()
                                # print  'cs:',self.connectedScore.keys()
                                # print  'ts:',self.totalScore.keys()
                                self.attributeScore[nn]+=2 ####属性出现频率加1，分数加2
                                #####更新最大属性分数
                                if self.attributeScore[nn] > self.maxaScore:
                                    self.maxaScore = self.attributeScore[nn]
            '5.更新总分（因为每一次最大分数都会变）(删除时候不更新，反正保持最大就行)'
            for n in self.connectedScore.keys():
                tmp = 0
                if self.maxcScore != 0 and self.maxaScore != 0:
                    tmp = self.alpha * (float(self.connectedScore[n]) / float(self.maxcScore)) + (1 - self.alpha) * (
                    float(self.attributeScore[n]) / float(self.maxaScore))
                elif self.maxcScore != 0:
                    tmp = self.alpha * (float(self.connectedScore[n]) / float(self.maxcScore))
                elif self.maxaScore != 0:
                    tmp = (1 - self.alpha) * (float(self.attributeScore[n]) / float(self.maxaScore))
                self.totalScore[n]=tmp
            return node


# def getBestNode(self):
#     '获得当前分数最大的节点'
#     ‘2017.3.30已改’
#     if len(self.totalScore) == 0:
#         return -1  ###已经没有候选节点了，返回-1
#     else:
#         maxItem = max(self.totalScore.items(), key=lambda x: x[1])  ##最大的选项
#         node = maxItem[0]
#         # score=maxItem[1]
#         '1.从待访问集合中删除'
#         # self.groupOfNodes[self.connectedScore[node]].remove(node)
#         del self.nodeGroup[node]
#         del self.connectedScore[node]
#         del self.attributeScore[node]
#         del self.totalScore[node]
#         '从候选属性集分组中删除'
#         for qa in self.queryAttrs:
#             if self.G.node[node].has_key('attr') and self.G.node[node]['attr'] != None:
#                 if qa in self.G.node[node]['attr']:
#                     self.queryAttrGroup[qa].remove(node)
#         '2.node加入solution之后，需要更新node邻居的连接数'
#         neighbors = self.G.neighbors(node)
#         for nei in neighbors:
#             if self.nodeGroup.has_key(nei):
#                 oldGroup = self.nodeGroup[nei]
#                 # self.groupOfNodes[oldGroup].remove(nei)
#                 newGroup = oldGroup + 1
#                 self.nodeGroup[nei] = newGroup
#                 self.connectedScore[nei] = newGroup  ##连接分数
#                 if newGroup > self.maxcScore:
#                     self.maxcScore = newGroup
#                     # self.groupOfNodes[newGroup].append(nei)
#         '3.node加入solution后，VwList需要更新,受影响属性分组下的节点的属性分数也要更新'
#         '更新VkList，更新最大属性分数'
#         for qa in self.queryAttrs:
#             if self.G.node[node].has_key('attr') and self.G.node[node]['attr'] != None:
#                 if qa in self.G.node[node]['attr']:  ##qa是受影响的查询属性
#                     self.VwList[qa] += 1  ###node与查询节点重合的属性出现频率需要
#                     #####node于qa交集的属性下的分组的属性分数需要更新，其他节点不受影响
#                     for nn in self.queryAttrGroup[qa]:
#                         self.attributeScore[nn] += 2  ####属性出现频率加1，分数加2
#                         #####更新最大属性分数
#                         if self.attributeScore[nn] > self.maxaScore:
#                             self.maxaScore = self.attributeScore[nn]
#         '5.更新总分（因为每一次最大分数都会变）(删除时候不更新，反正保持最大就行)'
#         for n in self.nodeGroup.keys():
#             tmp = 0
#             if self.maxcScore != 0 and self.maxaScore != 0:
#                 tmp = self.alpha * (float(self.connectedScore[n]) / float(self.maxcScore)) + (1 - self.alpha) * (
#                     float(self.attributeScore[n]) / float(self.maxaScore))
#             elif self.maxcScore != 0:
#                 tmp = self.alpha * (float(self.connectedScore[n]) / float(self.maxcScore))
#             elif self.maxaScore != 0:
#                 tmp = (1 - self.alpha) * (float(self.attributeScore[n]) / float(self.maxaScore))
#             self.totalScore[n] = tmp
#         return node
#
