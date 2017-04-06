# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:QulityEvaluation.py
@time:2017/3/410:08
@Function:质量评估
"""
from collections import defaultdict
import random
import networkx as nx

def dataReader(resFile,queryFile,labelFile):
    '读数据'
    '1.读取查询属性'
    queryAttrs = []
    qaf = open(queryFile, 'r')
    for line in qaf.readlines():
        line = line.strip()
        words = line.split()
        attrsStartid = words.index('attrs:')  ####查询属性开始的位置
        attrList = words[attrsStartid + 1:]
        queryAttrs.append(attrList)
    qaf.close()
    '2.读取相应的社团'
    communities = []
    size = []  # 社团大小
    cf = open(resFile, 'r')
    for line in cf.readlines():
        line = line.strip()
        words = line.split()
        communities.append(words)
        size.append(len(words))
    cf.close()
    print 'size:', size
    '3.读取节点的标签'
    nodeAttrDict = {}
    lq = open(labelFile, 'r')
    for line in lq.readlines():
        line = line.strip()
        words = line.split()
        nodeAttrDict[words[0]] = words[1:]
    lq.close()


def multiCMF(resFile,queryFile,labelFile):
    '一下子计算多个社团的CMF.读文件，注意结果文件与查询文件的每一行都是互相对应的'
    '1.读取查询属性'
    queryAttrs=[]
    qaf=open(queryFile,'r')
    for line in qaf.readlines():
        line=line.strip()
        words=line.split()
        attrsStartid=words.index('attr:') ####查询属性开始的位置
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
    # print 'size:',size
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
        # print '第',str(i),'次计算CMF，CPJ'
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
        if len(com)>0:
            for value in wordFreq.values():
                cmf+=float(value)/float(len(com))
        if len(aList)!=0:
            cmf=cmf/len(aList) ##防止除0
        CMFs[i]=cmf
        # print 'cmf:',cmf
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
                    jaccardSim+=tmpValue
        # print 'jaccard:',jaccardSim,' count:',count
        if count>0:
            jaccardSim=jaccardSim/count
        # print 'jaccardSim:',jaccardSim
        CPJs[i]=jaccardSim
    # print 'CMF:', CMFs
    # print 'CMF average:', sum(CMFs) / float(len(CMFs))
    # print 'CMF max:', max(CMFs)
    # print 'CPJ:', CPJs
    # print 'CPJ average', sum(CPJs) / float(len(CPJs))
    # print  'CPJ max:', max(CPJs)

    return CMFs,CPJs

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
        attrsStartid=words.index('attrs:') ####查询属性开始的位置
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

    # print 'CMF:',CMFs
    # print 'CMF average:',sum(CMFs)/float(len(CMFs))
    # print 'CMF max:',max(CMFs)
    # print 'CPJ:',CPJs
    # print 'CPJ average',sum(CPJs)/float(len(CPJs))
    # print  'CPJ max:',max(CPJs)

    return CMFs,CPJs







def run():
    path='L:/ACQData/'
    dataset='texas'
    algo='grdec/'
    queryFile=path+dataset+'_Query_wall.txt'
    labelFile=path+'inputfile/'+dataset+'_nodelabel'
    resFile=path+'cocktail/'+dataset+'_Query_wall_onlyNode_cocktail_res.txt'   ###cock的文件
    resFile2=path+algo+dataset+'_Query_wall_csm_res.txt' ##GreedyDec的文件
    resFile3=path+algo+dataset+'_Query_wall_cstGrd_k2_res.txt' ##GreedyDec的文件
    multiCMF(resFile2,queryFile,labelFile)

def runLDense():
    path='L:/ACQData/'
    dataset='delicious'
    queryFile=path+dataset+'_Query_wall.txt'
    labelFile=path+'inputfile/'+dataset+'_nodelabel'
    resFile='L:/ACQData/LDense/delicious/delicious_100'
    LDenseValuation(resFile,queryFile,labelFile)

def runGreedyDecV2csm():
    path='L:/ACQData/'
    # dataset='wisconsin'
    'Inc与dec切换'
    algo='greedyDecV2/'

    datasetList=['cornell','texas','wisconsin','washington','cora','citeseer']
    for dataset in datasetList:
        queryFile=path+'groundTruthData/'+dataset+'/'+dataset+'_query_2Nei_w3_100' ####查询文件
        labelFile=path+'groundTruthData/'+dataset+'/'+dataset+'_nodelabel'

        rescmfavg = []
        rescmfmax = []
        rescpjavg = []
        rescpjmax = []

        rescmfmin=[]
        rescpjmin=[]

        'inc 与dec切换'
        resFilecst = path + algo + dataset + '_query_2Nei_w3_100_csm_res.txt'  ##GreedyDec的文件
        # resFilecst = path + algo + dataset + '_query_2Nei_w3_100_csm_res_a5.txt'  ##GreedyDec的文件
        cmfList, cpjList = multiCMF(resFilecst, queryFile, labelFile)

        tmp1 = sum(cmfList) / float(len(cmfList))
        rescmfavg.append(tmp1)
        rescmfmax.append(max(cmfList))
        rescmfmin.append(min(cmfList))

        tmp2 = sum(cpjList) / float(len(cpjList))
        rescpjavg.append(tmp2)
        rescpjmax.append(max(cpjList))
        rescpjmin.append(min(cpjList))

        print "****************************************************"
        print 'data:',dataset
        print 'cmf min:',rescmfmin
        print 'cmf avg:', rescmfavg
        print 'cmf max:', rescmfmax
        print 'cpj min:',rescpjmin
        print 'cpj avg:', rescpjavg
        print 'cpj max:', rescpjmax


def runGreedyDecV2csmInc(dataset,alpha,queryTimes):
    path='L:/ACQData/'
    # dataset='wisconsin'
    'Inc与dec切换'
    algo='greedyInc'

    datasetList=['citeseer','cora','cornell','texas','wisconsin','washington']
    for dataset in datasetList:
        queryFile=path+'groundTruthData/'+dataset+'/'+dataset+'_query_2Nei_w3_'+str(queryTimes) ####查询文件
        labelFile=path+'groundTruthData/'+dataset+'/'+dataset+'_nodelabel'

        rescmf = {}

        rescpj = {}


        'inc 与dec切换'
        resFilecst = path + algo + dataset + '_query_2Nei_w3_'+str(queryTimes)+'_csm_res.txt'  ##GreedyDec的文件
        # resFilecst = path + algo + dataset + '_query_2Nei_w3_100_csm_res_a5.txt'  ##GreedyDec的文件
        cmfList, cpjList = multiCMF(resFilecst, queryFile, labelFile)

        tmp1 = sum(cmfList) / float(len(cmfList))
        rescmf['ave']=tmp1
        rescmf['max']=max(cmfList)
        rescmf['min']=min(cmfList)

        tmp2 = sum(cpjList) / float(len(cpjList))
        rescpj['ave']=tmp1
        rescpj['max']=max(cpjList)
        rescpj['min']=min(cpjList)

        # print "****************************************************"
        # print 'data:',dataset
        # print 'cmf min:',rescmfmin
        # print 'cmf avg:', rescmfavg
        # print 'cmf max:', rescmfmax
        # print 'cpj min:',rescpjmin
        # print 'cpj avg:', rescpjavg
        # print 'cpj max:', rescpjmax

        return  rescmf,rescpj



def runGreedyDecV2CST():
    path='L:/ACQData/'
    dataset='wisconsin'
    algo='greedyDecV2/'
    queryFile=path+'groundTruthData/'+dataset+'/'+dataset+'_query_2Nei_w3_100' ####查询文件
    labelFile=path+'groundTruthData/'+dataset+'/'+dataset+'_nodelabel'
    # resFile=path+'cocktail/'+dataset+'_Query_wall_onlyNode_cocktail_res.txt'   ###cock的文件
    # resFilecsm=path+algo+dataset+'_query_2Nei_w3_100_csm_res.txt' ##GreedyDec的文件
    # resFilecst=path+algo+dataset+'_query_2Nei_w3_100_k1_res.txt' ##GreedyDec的文件
    rescmfavg=[]
    rescmfmax=[]
    rescpjavg=[]
    rescpjmax=[]
    for k in range(1,5):
        resFilecst=path+algo+dataset+'_query_2Nei_w3_100_k'+str(k)+'_res.txt' ##GreedyDec的文件
        cmfList, cpjList = multiCMF(resFilecst, queryFile, labelFile)

        tmp1=sum(cmfList)/float(len(cmfList))
        rescmfavg.append(tmp1)
        rescmfmax.append(max(cmfList))

        tmp2=sum(cpjList)/float(len(cpjList))
        rescpjavg.append(tmp2)
        rescpjmax.append(max(cpjList))
    print 'cmf avg:',rescpjavg
    print 'cmf max:',rescmfmax
    print 'cpj avg:',rescpjavg
    print 'cmf max:',rescmfmax


def runGreedyDecV2csmFB():
    path='L:/ACQData/'
    # dataset='wisconsin'
    'Inc与dec切换'
    algo='greedyInc/'
    egoList = [0, 107, 348, 414, 686, 698, 1684, 1912, 3437, 3980]
    for ego in egoList:
        queryFile=path+'groundTruthData/facebook/facebook_ego'+str(ego)+'_query_1Nei_w3_10' ####查询文件
        labelFile=path+'groundTruthData/facebook/facebook_ego'+str(ego)+'_nodelabel'

        rescmfavg = []
        rescmfmax = []
        rescpjavg = []
        rescpjmax = []

        'inc 与dec切换'
        # resFilecst = path + algo +'facebook_ego'+str(ego)+ '_query_1Nei_w3_10_csm_res.txt'  ##GreedyDec的文件
        resFilecst = path + algo + 'facebook_ego' + str(ego) + '_query_1Nei_w3_10_csm_res_a5.txt'  ##GreedyInc的文件
        # resFilecst = path + algo + dataset + '_query_2Nei_w3_100_csm_res_a5.txt'  ##GreedyDec的文件
        cmfList, cpjList = multiCMF(resFilecst, queryFile, labelFile)

        tmp1 = sum(cmfList) / float(len(cmfList))
        rescmfavg.append(tmp1)
        rescmfmax.append(max(cmfList))

        tmp2 = sum(cpjList) / float(len(cpjList))
        rescpjavg.append(tmp2)
        rescpjmax.append(max(cpjList))

        print "****************************************************"
        print 'ego:',ego
        print 'cmf avg:', rescmfavg
        print 'cmf max:', rescmfmax
        print 'cpj avg:', rescpjavg
        print 'cpj max:', rescpjmax



def printallF1s(allavF1,allminF1,allmaxF1,dataList,alphaList):
    print 'allAvF1:'
    for data in dataList:
        alphaScores = allavF1[data]
        string = ''
        string += str(data) + '\t'
        for alpha in alphaList:
            score = alphaScores[alpha]
            string += str(score) + '\t'
        print string, '\n'

    print 'allmaxF1:'
    for data in dataList:
        alphaScores = allmaxF1[data]
        string = ''
        string += str(data) + '\t'
        for alpha in alphaList:
            score = alphaScores[alpha]
            string += str(score) + '\t'
        print string, '\n'

    print 'allminF1:'
    for data in dataList:
        alphaScores = allminF1[data]
        string = ''
        string += str(data) + '\t'
        for alpha in alphaList:
            score = alphaScores[alpha]
            string += str(score) + '\t'
        print string, '\n'




    '按F1分类打印'
    printallF1s(allavF1, allminF1, allmaxF1, dataList, alphaList)

if __name__=='__main__':
    # computeDensity()
    '普通的数据集'
    dataList=['citeseer','cora','cornell','texas','wisconsin','washington']
    alphaList=[0,2,4,6,8,10]
