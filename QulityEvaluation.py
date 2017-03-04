# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:QulityEvaluation.py
@time:2017/3/410:08
@Function:质量评估
"""
from collections import defaultdict
import random

def multiCMF(resFile,queryFile,labelFile):
    '一下子计算多个社团的CMF.读文件，注意结果文件与查询文件的每一行都是互相对应的'

    '1.读取查询属性'
    queryAttrs=[]
    qaf=open(queryFile,'r')
    for line in qaf.readlines():
        line=line.strip()
        words=line.split()
        attrsStartid=words.index('attrs:') ####查询属性开始的位置
        attrList=words[attrsStartid+1:]
        queryAttrs.append(attrList)
    qaf.close()
    '2.读取相应的社团'
    communities=[]
    size=[] #社团大小
    cf=open(resFile,'r')
    for line in cf.readlines():
        line=line.strip()
        words=line.split()
        communities.append(words)
        size.append(len(words))
    cf.close()
    print 'size:',size
    '3.读取节点的标签'
    nodeAttrDict={}
    lq=open(labelFile,'r')
    for line in lq.readlines():
        line=line.strip()
        words=line.split()
        nodeAttrDict[words[0]]=words[1:]
    lq.close()
    # '4.读取节点的邻居（adjlist格式）'
    # nodeNeighs={}
    # adjf=open(adjFile,'r')
    # for line in adjf.readlines():
    #     line=line.strip()
    #     words=line.split()
    #     nodeNeighs[words[0]]=words[1:]
    # adjf.close()
    '5.计算所有结果的CMF,CPJ'
    N=len(communities)
    CMFs=[0]*N
    CPJs=[0]*N
    for i in range(N):
        print '第',str(i),'次计算CMF，CPJ'
        com=communities[i]

        aList=queryAttrs[i] ##一排属性
        wordFreq={}

        '5.1：词频先初始化'
        for a in aList:
            wordFreq[a]=0
        '5.2：统计社团里面的词频'
        # jaccardSim=0
        for n in com:
            if nodeAttrDict.has_key(n):##可能会有节点没有属性
                ###统计查询属性出现的频率
                interset=[val for val in aList if val in nodeAttrDict[n]] #计算节点属性集合查询属性的交集
                for k in interset:
                    wordFreq[k]+=1

        '6:计算一个CMF'
        cmf=0.0
        for value in wordFreq.values():
            cmf+=float(value)/float(len(com))
        if len(aList)!=0:
            cmf=cmf/len(aList) ##防止除0
        CMFs[i]=cmf
        print 'cmf:',cmf
        '7.计算jaccard，若社团size>1000,社团中随机抽取1000个节点.否则直接两两进行计算'
        '7.1:社团抽样'
        comsize=len(com)
        nodeset=set()
        if comsize>1000:
            tmp=set()
            while(len(tmp)<1000):
                rid=random.randint(0,comsize-1)
                tmp.add(com[rid])
            nodeset=tmp
        else:
            nodeset=set(com)
        '7.2:计算两两节点之间的jaccard'
        jaccardSim=0.0
        count=0.0
        for nodeA in nodeset:
            for nodeB in nodeset:
                if(nodeA!=nodeB):
                    '计算两个节点的属性jaccard'
                    count+=1
                    tmpValue=0.0
                    share=0.0
                    attrSet=set()
                    for attrA in nodeAttrDict[nodeA]:
                        attrSet.add(attrA)
                    for attrB in nodeAttrDict[nodeB]:
                        if(attrB in attrSet):
                            share+=1
                        else:
                            attrSet.add(attrB)
                    if len(attrSet)!=0:
                        tmpValue=share/len(attrSet)
                    '加入最后结果'
                    jaccardSim+=tmpValue
        print 'jaccard:',jaccardSim,' count:',count
        jaccardSim=jaccardSim/count
        print 'jaccardSim:',jaccardSim
        CPJs[i]=jaccardSim

    print 'CMF:',CMFs
    print 'CPJ:',CPJs

def run():
    path='L:/ACQData/'
    dataset='dblps'
    algo='grdec/'
    queryFile=path+dataset+'_Query_wall.txt'
    labelFile=path+'inputfile/'+dataset+'_nodelabel'
    resFile=path+'cocktail/'+dataset+'_Query_wall_onlyNode_cocktail_res.txt'   ###cock的文件
    resFile2=path+algo+dataset+'_Query_wall_csm_res.txt' ##GreedyDec的文件
    multiCMF(resFile2,queryFile,labelFile)

if __name__=='__main__':
    run()
