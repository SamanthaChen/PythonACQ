# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:cocktailDealer.py
@time:2017/3/1414:41
@Function：处理cocktail party的
"""
from FMeasure import *
from QulityEvaluation import *

def cockTailF1evalution():
    '计算F1分数'
    path = 'L:/ACQData/groundTruthData/'
    data = 'wisconsin'
    dataName = data + '/' + data
    # edgePath = path + dataName + '_graph'
    classFile = open(path + dataName + '_class', 'r')
    labelFile = open(path + dataName + '_nodelabel', 'r')
    queryTimes=100
    queryFile = open(path + dataName + '_query_2Nei_w3_'+str(queryTimes), 'r')
    ####算法的结果文件
    resFile=open('L:/ACQData/cocktail/'+data+'_query_2Nei_w3_100_onlyNode_cocktail_res.txt','r')
    '读社团分组,节点class'
    # communityGroup = defaultdict(list)  ##社团分组
    nodeClassDict={}
    for line in classFile.readlines():
        line = line.strip()
        words = line.split()
        nodeClassDict[int(words[0])]=words[1]
        # communityGroup[words[1]].append(int(words[0]))
    classFile.close()
    '读节点属性'
    labelDict = {}
    for line in labelFile.readlines():
        line = line.strip()
        words = line.split()
        labelDict[int(words[0])] = words[1:]  ##属性还是str格式
    labelFile.close()
    '读结果文件'
    resComs=[]
    for line in resFile.readlines():
        line=line.strip()
        words=line.split()
        tmp=[int(val) for val in words]
        resComs.append(tmp)
    '读查询文件'
    querysList=[]
    # count=0
    for line in queryFile.readlines():
        line=line.strip()
        words=line.split()
        nodeStartId=words.index('node:')
        nodeEndId=words.index('attr:')
        tmp=words[nodeStartId+1:nodeEndId]
        tmp=[int(val) for val in tmp]
        querysList.append(tmp)
        # count+=1
    '计算F1Score'
    allF1Scores=[]
    # allPrecision=[]
    # allRecall=[]
    for i in range(len(resComs)):
        predCom=resComs[i]
        predlabel=[]
        ###真实的标签
        truelabel=[]
        trueclass=nodeClassDict[querysList[i][0]] ###第一个节点的class就是所有查询点的class（因为是在同一个class里面选的查询节点）
        for node in predCom:
            if nodeClassDict.has_key(node):
                if nodeClassDict[node]==trueclass:
                    truelabel.append(1)  ##与查询节点是一类的
                else:
                    truelabel.append(0)
            else:
                truelabel.append(1)
            ###预测的标签全都设为一类
            predlabel.append(1)
        f1=computeFScore(truelabel,predlabel)
        allF1Scores.append(f1)
        # allPrecision.append(precision)
        # allRecall.append(recall)
    print allF1Scores
    print len(allF1Scores)
    if len(allF1Scores)!=0:
        avrgf1=sum(allF1Scores)/float(len(allF1Scores))
    else:
        avrgf1=0
    # avrgprecision=sum(allPrecision)/float(len(allPrecision))
    # avrgrecall=sum(allRecall)/float(len(allRecall))
    print avrgf1
    print max(allF1Scores)
    # print avrgprecision
    # print avrgrecall

def cockTailF1():
    path = 'L:/ACQData/'
    # dataset='wisconsin'
    algo = 'cocktail/'

    datasetList = [ 'citeseer'] ##'cora', 'texas','cornell','wisconsin','washington',
    for dataset in datasetList:
        queryFile = path + 'groundTruthData/' + dataset + '/' + dataset + '_query_2Nei_w3_100'  ####查询文件
        labelFile = path + 'groundTruthData/' + dataset + '/' + dataset + '_nodelabel'

        rescmfavg = []
        rescmfmax = []
        rescpjavg = []
        rescpjmax = []

        resFile = path + algo + dataset + '_query_2Nei_w3_100_onlyNode_cocktail_res.txt'  ##cocktailParty
        cmfList, cpjList = multiCMF(resFile, queryFile, labelFile)

        tmp1 = sum(cmfList) / float(len(cmfList))
        rescmfavg.append(tmp1)
        rescmfmax.append(max(cmfList))

        tmp2 = sum(cpjList) / float(len(cpjList))
        rescpjavg.append(tmp2)
        rescpjmax.append(max(cpjList))

        print "****************************************************"
        print 'data:', dataset
        print 'cmf avg:', rescmfavg
        print 'cmf max:', rescmfmax
        print 'cpj avg:', rescpjavg
        print 'cpj max:', rescpjmax


if __name__=='__main__':
    # cockTailF1evalution()
    cockTailF1()