# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:cocktailDealer.py
@time:2017/3/1414:41
@Function：处理cocktail party的
"""
from FMeasureV2 import *
from QulityEvaluationV2 import *

def cockTailF1evalution():
    '计算F1分数'
    dataList = ['citeseer', 'cora', 'cornell', 'texas', 'wisconsin', 'washington']
    allavF1 = {}
    allminF1 = {}
    allmaxF1 = {}
    for data in dataList:
        '读各个文件'
        path = 'L:/ACQData/groundTruthData/'
        # data = 'wisconsin'
        dataName = data + '/' + data
        # edgePath = path + dataName + '_graph'
        classFile = open(path + dataName + '_class', 'r')
        labelFile = open(path + dataName + '_nodelabel', 'r')
        queryTimes = 10
        queryFile = open(path + dataName + '_query_2Nei_w3_' + str(queryTimes), 'r')
        ####算法的结果文件
        resFile = open(
            'L:/ACQData/cocktail/' + data + '_query_2Nei_w3_' + str(queryTimes) + '_onlyNode_cocktail_res.txt', 'r')

        '计算F1'
        avF1, minF1, maxF1 = computeF1Scores(classFile,labelFile,resFile,queryFile)

        allavF1[data] = avF1
        allminF1[data] = minF1
        allmaxF1[data] = maxF1

    '打印总分'
    print 'data\tmin\t\ave\tmax'
    for data in dataList:
        print data, '\t', allminF1[data], '\t', allavF1[data], '\t', allmaxF1[data]


def cockTailF1evalutionFB():
    '计算F1分数'
    egoList=[0,107,348,414,686,698,1684,1912,3437,3980]
    allavF1 = {}
    allminF1 = {}
    allmaxF1 = {}
    for ego in egoList:
        '读各个文件'
        path = 'L:/ACQData/groundTruthData/'
        # data = 'wisconsin'
        dataName =   'facebook/facebook'
        # edgePath = path + dataName + '_graph'
        classFile = open(path + dataName + '_ego'+str(ego)+'_class', 'r')
        labelFile = open(path + dataName + '_ego'+str(ego)+ '_nodelabel', 'r')
        queryTimes = 10
        queryFile = open(path + dataName +  '_ego'+str(ego)+'_query_1Nei_w3_' + str(queryTimes), 'r')
        ####算法的结果文件
        resFile = open(
            'L:/ACQData/cocktail/facebook_ego' +str(ego)  + '_query_1Nei_w3_' + str(queryTimes) + '_onlyNode_cocktail_res.txt', 'r')

        '计算F1'
        avF1, minF1, maxF1 = computeF1ScoresFB(ego,classFile,labelFile,resFile,queryFile)

        allavF1[ego] = avF1
        allminF1[ego] = minF1
        allmaxF1[ego] = maxF1

    '打印总分'
    print 'data\tmin\t\ave\tmax'
    for data in egoList:
        print data, '\t', allminF1[data], '\t', allavF1[data], '\t', allmaxF1[data]

def computeF1Scores(classFile,labelFile,resFile,queryFile):
    '读社团分组'
    # communityGroup = defaultdict(list)  ##社团分组
    nodeClassDict = {}
    for line in classFile.readlines():
        line = line.strip()
        words = line.split()
        nodeClassDict[int(words[0])] = words[1]
        # communityGroup[words[1]].append(int(words[0]))
    classFile.close()
    '读节点标签'
    labelDict = {}
    for line in labelFile.readlines():
        line = line.strip()
        words = line.split()
        labelDict[int(words[0])] = words[1:]  ##属性还是str格式
    labelFile.close()
    '读结果文件'
    lineResDict = {}
    lineCount = 0
    for line in resFile.readlines():
        line = line.strip()
        if not line.startswith('No'):
            words = line.split()
            tmp = [int(val) for val in words]
            lineResDict[lineCount] = tmp
        lineCount += 1
    '读查询文件'
    querysList = []
    # count=0
    for line in queryFile.readlines():
        line = line.strip()
        words = line.split()
        nodeStartId = words.index('node:')
        nodeEndId = words.index('attr:')
        tmp = words[nodeStartId + 1:nodeEndId]
        tmp = [int(val) for val in tmp]
        querysList.append(tmp)
        # count+=1
    '计算F1Score'
    allF1Scores = []
    # allPrecision=[]
    # allRecall=[]
    for id in lineResDict.keys():
        predCom = lineResDict[id]
        predlabel = []
        ###真实的标签
        truelabel = []
        '-------------------------------------------------'
        '查询节点的类都设为真实标签1，其他节点都设成0'
        queryLabels = [] #查询节点标签列表
        for q in querysList[id]:
            queryLabels.append(nodeClassDict[q])
        '设置标签'
        for node in predCom:
            truelabel.append(1)
            if nodeClassDict.has_key(node) and nodeClassDict[node] in queryLabels:
                predlabel.append(1)
            else:
                predlabel.append(0)
        '-------------------------------------------------'
        f1 = computeFScore(truelabel, predlabel)
        allF1Scores.append(f1)
        # allPrecision.append(precision)
        # allRecall.append(recall)
    # print 'allF1Scores:',allF1Scores
    # print 'len(allF1Scores):',len(allF1Scores)
    if len(allF1Scores) != 0:
        avrgf1 = sum(allF1Scores) / float(len(allF1Scores))
    else:
        avrgf1 = 0

    return avrgf1, min(allF1Scores), max(allF1Scores)


def computeF1ScoresFB(ego,classFile,labelFile,resFile,queryFile):
    '读社团分组'
    # communityGroup = defaultdict(list)  ##社团分组
    nodeClassDict = {}
    for line in classFile.readlines():
        line = line.strip()
        words = line.split()
        nodeClassDict[int(words[0])] = words[1]
        # communityGroup[words[1]].append(int(words[0]))
    classFile.close()
    '读节点标签'
    labelDict = {}
    for line in labelFile.readlines():
        line = line.strip()
        words = line.split()
        labelDict[int(words[0])] = words[1:]  ##属性还是str格式
    labelFile.close()
    '读结果文件'
    lineResDict = {}
    lineCount = 0
    for line in resFile.readlines():
        line = line.strip()
        if not line.startswith('No'):
            words = line.split()
            tmp = [int(val) for val in words]
            lineResDict[lineCount] = tmp
        lineCount += 1
    '读查询文件'
    querysList = []
    # count=0
    for line in queryFile.readlines():
        line = line.strip()
        words = line.split()
        nodeStartId = words.index('node:')
        nodeEndId = words.index('attr:')
        tmp = words[nodeStartId + 1:nodeEndId]
        tmp = [int(val) for val in tmp]
        querysList.append(tmp)
        # count+=1
    '计算F1Score'
    allF1Scores = []
    # allPrecision=[]
    # allRecall=[]
    for id in lineResDict.keys():
        predCom = lineResDict[id]
        predlabel = []
        ###真实的标签
        truelabel = []
        '-------------------------------------------------'
        '查询节点的类都设为真实标签1，其他节点都设成0'
        queryLabels = [] #查询节点标签列表
        for q in querysList[id]:
            if nodeClassDict.has_key(q):
                queryLabels.append(nodeClassDict[q])
        '设置标签'
        for node in predCom:
            truelabel.append(1)
            if not nodeClassDict.has_key(node) or nodeClassDict[node] in queryLabels :
                predlabel.append(1)
            else:
                predlabel.append(0)
        '-------------------------------------------------'
        f1 = computeFScore(truelabel, predlabel)
        allF1Scores.append(f1)
        # allPrecision.append(precision)
        # allRecall.append(recall)
    # print 'allF1Scores:',allF1Scores
    # print 'len(allF1Scores):',len(allF1Scores)
    if len(allF1Scores) != 0:
        avrgf1 = sum(allF1Scores) / float(len(allF1Scores))
    else:
        avrgf1 = 0

    return avrgf1, min(allF1Scores), max(allF1Scores)

def cockTailCMFevalution():
    '计算F1分数'
    dataList = ['citeseer', 'cora', 'cornell', 'texas', 'wisconsin', 'washington']
    dataList2=['dblps']
    allavF1 = {}
    allminF1 = {}
    allmaxF1 = {}
    for data in dataList2:
        '读各个文件'
        path = 'L:/ACQData/inputfile/'
        # data = 'wisconsin'
        dataName = data + '/' + data
        # edgePath = path + dataName + '_graph'
        classFile = path + dataName + '_class'
        labelFile = path + dataName + '_nodelabel'
        queryTimes = 1
        queryFile = path + dataName + '_query_randomcore_w3_' + str(queryTimes)+'.txt'
        ####算法的结果文件
        resFile =  'L:/ACQData/cocktail/' + data + '_query_randomcore_w3_' + str(queryTimes) + '_onlyNode_cocktail_res.txt'

        '计算F1'
        avF1, minF1, maxF1 =  multiCMF(resFile, queryFile, labelFile)
           ## computeF1Scores(classFile,labelFile,resFile,queryFile)

        allavF1[data] = avF1
        allminF1[data] = minF1
        allmaxF1[data] = maxF1

    '打印总分'
    print 'data\tmin\t\ave\tmax'
    for data in dataList2:
        print data, '\t', allminF1[data], '\t', allavF1[data], '\t', allmaxF1[data]

def cockTailCMFevalutionFB():
    '计算F1分数'
    egoList  = [0, 107, 348, 414, 686, 698, 1684, 1912, 3437, 3980]
    allavF1 = {}
    allminF1 = {}
    allmaxF1 = {}
    for ego in egoList:
        '读各个文件'
        path = 'L:/ACQData/groundTruthData/'
        # data = 'wisconsin'
        dataName = 'facebook/facebook'
        # edgePath = path + dataName + '_graph'
        classFile = path + dataName + '_ego' + str(ego) + '_class'
        labelFile = path + dataName + '_ego' + str(ego) + '_nodelabel'
        queryTimes = 10
        queryFile = path + dataName + '_ego' + str(ego) + '_query_1Nei_w3_' + str(queryTimes)
        ####算法的结果文件
        resFile = 'L:/ACQData/cocktail/facebook_ego' + str(ego) + '_query_1Nei_w3_' + str(
                queryTimes) + '_onlyNode_cocktail_res.txt'

        '计算F1'
        avF1, minF1, maxF1 =  multiCMF(resFile, queryFile, labelFile)
           ## computeF1Scores(classFile,labelFile,resFile,queryFile)

        allavF1[ego] = avF1
        allminF1[ego] = minF1
        allmaxF1[ego] = maxF1

    '打印总分'
    print 'data\tmin\t\ave\tmax'
    for data in egoList:
        print data, '\t', allminF1[data], '\t', allavF1[data], '\t', allmaxF1[data]



if __name__=='__main__':
    # cockTailF1evalutionFB()
    cockTailCMFevalution()
    # cockTailF1evalutionFB()