# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:LDenseDealer.py
@time:2017/3/516:15
@Function：处理LDense的
"""
from FMeasure import *
import random
####处理LDense的
###4的倍数行存的是社团
def raw2Community():
    data='washington'
    rFile=open( 'L:/ACQData/LDense/' +data+'/'+data+'_all_A.lo_100.communities','r')
    wFile=open('L:/ACQData/LDense/' +data+'/'+data+'_100','w')
    lineNum=1
    for line in rFile.readlines():
        if(lineNum%4==0):
            line=line.replace(' (','')
            line=line.replace(',','')
            line=line.replace(')','')
            line.strip()
            wFile.write(line)
        lineNum+=1

def LDenseF1Valuation():
    'LDense的F1精确度评估'
    path = 'L:/ACQData/'
    dataset = 'washington'
    queryFile = path + 'groundTruthData/'+dataset + '/'+dataset+'_query_2Nei_w3_100'
    # labelFile = path +  'groundTruth/'+dataset + '/'+dataset + '_nodelabel'
    classFile = path +  'groundTruthData/'+dataset + '/'+dataset + '_class'
    resFile = path+'LDense/'+dataset + '/'+dataset+'_100'

    '评估LDense'
    '1:把社团读进来'
    communityList=[]
    resf=open(resFile,'r')
    for line in resf.readlines():
        line=line.strip()
        words=line.split()
        com=[int(val) for val in words]
        communityList.append(com)
    resf.close()
    '2:读查询节点，查询属性。'
    queryAttrs=[]
    queryNodes=[]
    qaf=open(queryFile,'r')
    for line in qaf.readlines():
        line=line.strip()
        words=line.split()
        nodeStartid=words.index('node:')
        attrsStartid=words.index('attr:') ####查询属性开始的位置
        attrList=words[attrsStartid+1:]
        nodeList=[int(val) for val in words[nodeStartid+1:attrsStartid]]
        queryAttrs.append(attrList)
        queryNodes.append(nodeList)
    qaf.close()
    # '3.读取节点的标签'
    # nodeAttrDict={}
    # lq=open(labelFile,'r')
    # for line in lq.readlines():
    #     line=line.strip()
    #     words=line.split()
    #     nodeAttrDict[int(words[0])]=words[1:]
    # lq.close()
    '4:确定涉及查询节点的社团'
    relatedComs=[]
    for j in range(len(queryNodes)):
        nodeList=queryNodes[j] ###查询的节点列表
        comSet=set()
        for n in nodeList:
            for i in range(len(communityList)):
                if n in communityList[i]:
                    comSet.add(i)
        relatedComs.append(list(comSet))
    '5:读节点所在class'
    cf=open(classFile,'r')
    nodeClassDict={}
    for line in cf.readlines():
        line=line.strip()
        words=line.split()
        nodeClassDict[int(words[0])]=words[1]
    cf.close()
    '6:计算F1'
    allF1Scores=[]

    for i in range(len(relatedComs)):
        comIDSet=relatedComs[i] ###第i行查询设计的节点ID列表
        querysList=queryNodes[i] ###第i行查询设计的节点ID
        f1List=[] ###多个社团的f1
        for comID in comIDSet:
            predCom=communityList[comID]
            ##计算每个社团的f1
            predlabel = []
            ###真实的标签
            truelabel = []
            trueclass = nodeClassDict[querysList[0]]  ###因为选出来的查询节点都在一个社团
            for node in predCom:
                if nodeClassDict.has_key(node):
                    if nodeClassDict[node] == trueclass:
                        truelabel.append(1)  ##与查询节点
                    else:
                        truelabel.append(0)
                else:
                    truelabel.append(1)
            ###预测的标签全都设为一类
                predlabel.append(1)
            f1 = computeFScore(truelabel, predlabel)          ##一个相关社团的f1
            f1List.append(f1)
        ###计算这一串社团平均的f1
        tmp=0
        if len(f1List)>0:
            tmp=float(sum(f1List))/float(len(f1List))       ###多个相关社团的F1
        allF1Scores.append(tmp)
    print allF1Scores
    print len(allF1Scores)
    if len(allF1Scores) != 0:
        avrgf1 = sum(allF1Scores) / float(len(allF1Scores))
    else:
        avrgf1 = 0
    # avrgprecision=sum(allPrecision)/float(len(allPrecision))
    # avrgrecall=sum(allRecall)/float(len(allRecall))
    print avrgf1
    print max(allF1Scores)
    # print avrgprecision
    # print avrgrecall

def LDenseValuation(resFile,queryFile,labelFile):
    '评估LDense的CMF，注意一个查询条件会得出多个相关社团'
    '1:把社团读进来'
    communityList=[]
    resf=open(resFile,'r')
    for line in resf.readlines():
        line=line.strip()
        words=line.split()
        com=[int(val) for val in words]
        communityList.append(com)
    resf.close()
    '2:读查询节点，查询属性。'
    queryAttrs=[]
    queryNodes=[]
    qaf=open(queryFile,'r')
    for line in qaf.readlines():
        line=line.strip()
        words=line.split()
        nodeStartid=words.index('node:')
        attrsStartid=words.index('attr:') ####查 询属性开始的位置
        attrList=words[attrsStartid+1:]
        nodeList=[int(val) for val in words[nodeStartid+1:attrsStartid]]
        queryAttrs.append(attrList)
        queryNodes.append(nodeList)
    qaf.close()
    '3.读取节点的标签'
    nodeAttrDict={}
    lq=open(labelFile,'r')
    for line in lq.readlines():
        line=line.strip()
        words=line.split()
        nodeAttrDict[int(words[0])]=words[1:]
    lq.close()
    '4:确定涉及查询节点的社团'
    relatedComs=[]
    for j in range(len(queryNodes)):
        nodeList=queryNodes[j]
        comSet=set()
        for n in nodeList:
            for i in range(len(communityList)):
                if n in communityList[i]:
                    comSet.add(i)
        relatedComs.append(list(comSet))
    '5.计算所有结果的CMF'
    N=len(queryNodes)
    CMFs=[0]*N
    CPJs=[0]*N
    for i in range(N):
        # print '第',str(i),'次计算CMF，CPJ'
        comIDList=relatedComs[i]
        aList=queryAttrs[i] ##一排查询属性
        wordFreq={}

        '5.2：统计社团里面的词频'
        cmf=0.0
        for comID in comIDList:
            com=communityList[comID]
            '5.2.1：词频先初始化'
            for a in aList:
                wordFreq[a]=0
            '5.2.1：计算一个社团内出现的频率'
            for n in com:
                if nodeAttrDict.has_key(n):##可能会有节点没有属性
                    ###统计查询属性出现的频率
                    interset=[val for val in aList if val in nodeAttrDict[n]] #计算节点属性集合查询属性的交集
                    for k in interset:
                        wordFreq[k]+=1
            '5.2.2:计算一个CMF'
            for value in wordFreq.values():
                cmf+=float(value)/float(len(com))

        if len(aList)!=0 and len(comIDList)!=0:
                cmf=cmf/len(aList)/len(comIDList) ##防止除0

        CMFs[i]=cmf
        # print 'cmf:',cmf

        '7.计算jaccard，若社团size>1000,社团中随机抽取1000个节点.否则直接两两进行计算'
        jaccardSim=0.0
        for comID in comIDList:
            '7.1:社团抽样'
            com=communityList[comID]
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
            count=0.0
            Sim=0.0
            for nodeA in nodeset:
                for nodeB in nodeset:
                    if(nodeA!=nodeB):
                        '计算两个节点的属性jaccard'
                        count+=1
                        tmpValue=0.0
                        share=0.0
                        attrSet=set()
                        if nodeAttrDict.has_key(nodeA):
                            for attrA in nodeAttrDict[nodeA]:
                                attrSet.add(attrA)
                        if nodeAttrDict.has_key(nodeB):
                            for attrB in nodeAttrDict[nodeB]:
                                if(attrB in attrSet):
                                    share+=1
                                else:
                                    attrSet.add(attrB)
                        if len(attrSet)!=0:
                            tmpValue=share/len(attrSet)
                        '加入最后结果'
                        Sim+=tmpValue
            # print 'jaccard:',jaccardSim,' count:',count
            if count!=0:
                jaccardSim+=Sim/count
        # print 'jaccardSim:',jaccardSim
        if len(comIDList)!=0:
            jaccardSim=jaccardSim/len(comIDList)
        # print 'jaccardSim:',jaccardSim
        CPJs[i]=jaccardSim

    print 'CMF:',CMFs
    print 'CMF average:', sum(CMFs)/float(len(CMFs))
    print 'CMF max:',max(CMFs)
    print 'CPJ:',CPJs
    print 'CPJ average',sum(CPJs)/float(len(CPJs))
    print  'CPJ max:',max(CPJs)

    return CMFs,CPJs


def runLDenseCMF():
    path = 'L:/ACQData/'
    dataset = 'cora'
    queryFile = path + 'groundTruthData/'+dataset +'/'+dataset+ '_query_2Nei_w3_100'
    labelFile = path + 'groundTruthData/'+dataset +'/'+dataset + '_nodelabel'
    resFile = 'L:/ACQData/LDense/'+dataset+'/'+dataset+'_100'
    LDenseValuation(resFile, queryFile, labelFile)


if __name__=='__main__':
    # raw2Community()
    # LDenseF1Valuation()
    runLDenseCMF()