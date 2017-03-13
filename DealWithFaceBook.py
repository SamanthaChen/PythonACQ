# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:DealWithFaceBook.py
@time:2017/3/1320:16
@Function:处理跟facebook有关的数据
"""
from collections import defaultdict
if __name__=='__main__':
    ego=0
    path='L:/ACQData/groundTruthData/facebook/facebook/'
    ####读取的文件
    edgesFile=open(path+str(ego)+'.edges','r')
    otherfeatFile=open(path+str(ego)+'.feat','r')
    egofeatFile=open(path+str(ego)+'.egofeat','r')
    circlesFile=open(path+str(ego)+'.circles','r')
    ######写入的文件
    graphFile=open(path+'facebook_ego'+str(ego)+'_graph','w')
    nodelabelFile=open(path+'facebook_ego'+str(ego)+'_nodelabel','w')

    '读取除了ego外的所有的节点，和节点的标签，生成属性链表'
    nodes=set()
    nodeLabelDict=defaultdict(list)
    for line in otherfeatFile.readlines():
        line=line.strip()
        words=line.split()
        u=int(words[0])
        nodes.add(u)
        attrs=[int(val) for val in words[1:]]
        for i in range(len(attrs)):
            if attrs[i]==1:
                nodeLabelDict[u].append(i) ##用数字型的吗？？还是str的？？
    otherfeatFile.close()
    '读ego的标签，添加到nodeLabelDict中'
    for line in egofeatFile.readlines():
        line=line.strip()
        words=line.split()
        attrs=[int(val) for val in words]
        for i in range(len(attrs)):
            if attrs[i]==1:
                nodeLabelDict[ego].append(i) ##用数字型的吗？？还是str的？？
    egofeatFile.close()
    '读除了ego外的边,生成邻居链表(这个数据好像一条边存两次)'
    adjList=defaultdict(list)
    for line in edgesFile.readlines():
        line=line.strip()
        words=line.split()
        u=int(words[0])
        v=int(words[1])
        if adjList.has_key(u):
            adjList[u].append(v)
    edgesFile.close()
    '创造ego到所有其他节点的边'
    tmp=nodeLabelDict.keys()
    tmp.remove(ego)
    adjList[ego]=tmp
    '写入边文件文件'
    for node,neighbors in adjList.items():
        string=''
        string+=node
        for nei in neighbors:
            string+=' '+nei
        graphFile.write(string+'\n')
    graphFile.close()
    '写入节点属性文件'
    for node,attrs in nodeLabelDict.items():
        string=''
        string+=node
        for a in attrs:
            string+=' '+a
        nodelabelFile.write(string+'/n')
    nodelabelFile.close()













