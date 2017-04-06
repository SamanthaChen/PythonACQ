# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:FMeasure.py
@time:2017/3/1217:10

第一个版本的FMeasure针对的是从同一个类中选出查询节点的文件
这个版本的FMeasure针对随机选的
"""
from collections import defaultdict
import networkx as nx

def computeFScore(truelabel,predlabel):
    '计算两个社团的F1.输入是两个List'
    interSectLen=0.0
    for i in range(len(truelabel)):
        if truelabel[i]==predlabel[i]:
            interSectLen+=1.0
    precision=0
    recall=0
    F1Score=0
    if len(predlabel)>0:
        precision=interSectLen/float(len(predlabel))
    if len(truelabel)>0:
        recall=interSectLen/float(len(truelabel))
    if precision+recall>0:
        F1Score=(2*precision*recall)/(precision+recall)
    return F1Score


def computeF1Dec(data,queryTimes):
    path = 'L:/ACQData/groundTruthData/'
    # data = 'citeseer'
    dataName = data + '/' + data
    # edgePath = path + dataName + '_graph'
    classFile = open(path + dataName + '_class', 'r')
    labelFile = open(path + dataName + '_nodelabel', 'r')
    # queryTimes=100
    queryFile = open(path + dataName + '_query_2Nei_w3_'+str(queryTimes), 'r')
    ####算法的结果文件
    resFile=open('L:/ACQData/greedyDecV2/'+data+'_query_2Nei_w3_'+str(queryTimes)+'_csm_res.txt','r')
    '读社团分组'
    # communityGroup = defaultdict(list)  ##社团分组
    nodeClassDict={}
    for line in classFile.readlines():
        line = line.strip()
        words = line.split()
        nodeClassDict[int(words[0])]=words[1]
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
    lineResDict={}
    lineCount=0
    for line in resFile.readlines():
        line=line.strip()
        if not line.startswith('No'):
            words=line.split()
            tmp=[int(val) for val in words]
            lineResDict[lineCount]=tmp
        lineCount+=1
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
    for id in lineResDict.keys():
        predCom=lineResDict[id]
        predlabel=[]
        ###真实的标签
        truelabel=[]
        '-------------------------------------------------'
        '查询节点的类都设为真实标签1，其他节点都设成0'
        queryLabels = []
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
        f1=computeFScore(truelabel,predlabel)
        allF1Scores.append(f1)
        # allPrecision.append(precision)
        # allRecall.append(recall)
    # print 'allF1Scores:',allF1Scores
    # print 'len(allF1Scores):',len(allF1Scores)
    if len(allF1Scores)!=0:
        avrgf1=sum(allF1Scores)/float(len(allF1Scores))
    else:
        avrgf1=0

    return avrgf1, min(allF1Scores), max(allF1Scores)

def computeF1Inc(data,queryTimes,alpha):
    '''
    计算Inc的
    :param data:
    :param queryTimes:
    :param alpha:
    :return:
    '''
    path = 'L:/ACQData/groundTruthData/'
    # data = 'citeseer'
    dataName = data + '/' + data
    # edgePath = path + dataName + '_graph'
    classFile = open(path + dataName + '_class', 'r')
    labelFile = open(path + dataName + '_nodelabel', 'r')
    # queryTimes=100
    # queryFile = open(path + dataName + '_query_core3_w3_'+str(queryTimes), 'r')
    queryFile = open(path + dataName + '_query_2Nei_w3_test', 'r')
    ####算法的结果文件
    # resFile=open('L:/ACQData/greedyInc/'+data+'_query_core2_w3_'+str(queryTimes)+'_csm_res_a'+str(alpha)+'.txt','r')
    resFile = open(
        'L:/ACQData/greedyInc/' + data + '_query_2Nei_w3_test_csm_res_a' + str(alpha) + '.txt', 'r')
    '读社团分组'
    # communityGroup = defaultdict(list)  ##社团分组
    nodeClassDict={}
    for line in classFile.readlines():
        line = line.strip()
        words = line.split()
        nodeClassDict[int(words[0])]=words[1]
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
    lineResDict={}
    lineCount=0
    for line in resFile.readlines():
        line=line.strip()
        if not line.startswith('No'):
            words=line.split()
            tmp=[int(val) for val in words]
            lineResDict[lineCount]=tmp
        lineCount+=1
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
    for id in lineResDict.keys():
        predCom=lineResDict[id]
        predlabel=[]
        ###真实的标签
        truelabel=[]
        '-------------------------------------------------'
        '查询节点的类都设为真实标签1，其他节点都设成0'
        queryLabels = []
        for q in querysList[id]:
            queryLabels.append(nodeClassDict[q])
        '设置标签'
        for node in predCom:
            truelabel.append(1)
            if not nodeClassDict.has_key(node) or nodeClassDict[node] in queryLabels:
                predlabel.append(1)
            else:
                predlabel.append(0)
        '-------------------------------------------------'
        f1=computeFScore(truelabel,predlabel)
        allF1Scores.append(f1)
        # allPrecision.append(precision)
        # allRecall.append(recall)
    # print 'allF1Scores:',allF1Scores
    # print 'len(allF1Scores):',len(allF1Scores)
    if len(allF1Scores)!=0:
        avrgf1=sum(allF1Scores)/float(len(allF1Scores))
    else:
        avrgf1=0
    # avrgprecision=sum(allPrecision)/float(len(allPrecision))
    # avrgrecall=sum(allRecall)/float(len(allRecall))
    # print 'avrgf1:',avrgf1
    # print 'min(allF1Scores):',min(allF1Scores)
    # print 'max(allF1Scores):',max(allF1Scores)
    # print avrgprecision
    # print avrgrecall
    return avrgf1,min(allF1Scores),max(allF1Scores)


def egoNetworkF1Dec(ego,queryTimes):
    '查询节点不一定从一个类中选出来的'
    path = 'L:/ACQData/groundTruthData/'
    data = 'facebook'
    dataName = data + '/' + data
    edgeFile = path + dataName + '_ego'+str(ego)+'_graph'
    classFile = open(path + dataName + '_ego'+str(ego)+'_class', 'r')
    labelFile = open(path + dataName + '_ego'+str(ego)+'_nodelabel', 'r')
    queryFile = open(path + dataName +'_ego'+str(ego)+ '_query_1Nei_w3_10', 'r')
    ####算法的结果文件

    resFile = open('L:/ACQData/greedyDecV2/' + data + '_ego'+str(ego)+'_query_1Nei_w3_10_csm_res.txt', 'r') ####csm+greedyInc
    '读图'
    G=nx.Graph()
    G=nx.read_adjlist(edgeFile,nodetype=int)
    '读社团分组'
    # communityGroup = defaultdict(list)  ##社团分组
    nodeClassDict = {}
    for line in classFile.readlines():
        line = line.strip()
        words = line.split()
        nodeClassDict[int(words[0])] = words[1]
        # communityGroup[words[1]].append(int(words[0]))
    classFile.close()
    '假设图中还有节点没有属性'
    for node in G.nodes():
        if node not in nodeClassDict.keys():
            for key in nodeClassDict.keys():
                nodeClassDict[node]=key
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
        '注意facebook的网络社团是重叠的'
        predlabel = []
        ###真实的标签
        truelabel = []
        '查询节点个数大于1,才有可能包含除了ego节点外的其他节点'
        queryNodes=querysList[id]  #查询节点
        if len(queryNodes)>0:
            '-------------------------------------------------'
            '查询节点的类都设为真实标签1，其他节点都设成0'
            queryLabels = []
            for q in querysList[id]:
                if q!=ego:
                    queryLabels.append(nodeClassDict[q])
            '设置标签'
            for node in predCom:
                truelabel.append(1)
                if node==ego or nodeClassDict[node] in queryLabels :
                    predlabel.append(1)
                else:
                    predlabel.append(0)
            '-------------------------------------------------'
            f1 = computeFScore(truelabel, predlabel)
        else:####只有一个查询节点，说明只有ego直接返回1
            f1=1

        allF1Scores.append(f1)
        # allPrecision.append(precision)
        # allRecall.append(recall)
    # print allF1Scores
    # print len(allF1Scores)
    avergf1=0.0
    if len(allF1Scores) != 0:
        avrgf1 = sum(allF1Scores) / float(len(allF1Scores))
    minf1=0.0
    maxf1=0.0
    if len(allF1Scores)>0:
        maxf1= max(allF1Scores)
        minf1=min(allF1Scores)
    return avrgf1,minf1,maxf1

def egoNetworkIncF1(ego,alpha,queryTimes):
    '适用于查询节点是从一个类 中选出来的'
    path = 'L:/ACQData/groundTruthData/'
    data = 'facebook'
    dataName = data + '/' + data
    # edgePath = path + dataName + '_graph'
    classFile = open(path + dataName + '_ego'+str(ego)+'_class', 'r')
    labelFile = open(path + dataName + '_ego'+str(ego)+'_nodelabel', 'r')
    # queryTimes = 10
    queryFile = open(path + dataName +'_ego'+str(ego)+ '_query_core3_w3_10' , 'r')
    ####算法的结果文件
    # resFile = open('L:/ACQData/greedyDecV2/' + data + '_ego'+str(ego)+'_query_1Nei_w3_10_csm_res.txt', 'r') ####csm+greedyDec
    # resFile = open('L:/ACQData/greedyDecV2/' + data + '_ego'+str(ego)+'_query_1Nei_w3_10_k'+str(k)+'_res.txt', 'r') ####cst+greedyDec
    resFile = open('L:/ACQData/greedyInc/' + data + '_ego'+str(ego)+'_query_core3_w3_10_csm_res_a'+str(alpha)+'.txt', 'r') ####csm+greedyInc
    # resFile = open('L:/ACQData/greedyInc/' + data + '_ego' + str(ego) + '_query_1Nei_w3_10_k' + str(k) + '_res_a5.txt',  ###cst+greedyInc
    #                'r')
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
        '注意facebook的网络社团是重叠的'
        predlabel = []
        ###真实的标签
        truelabel = []
        '查询节点个数大于1,才有可能包含除了ego节点外的其他节点'
        queryNodes=querysList[id]
        if len(queryNodes)>0:
            '-------------------------------------------------'
            '查询节点的类都设为真实标签1，其他节点都设成0'
            queryLabels = []
            for q in querysList[id]:
                if nodeClassDict.has_key(q):
                    queryLabels.append(nodeClassDict[q])
            '设置标签'
            for node in predCom:
                truelabel.append(1)
                if node==ego or not nodeClassDict.has_key(node) or nodeClassDict[node] in queryLabels :
                    predlabel.append(1)
                else:
                    predlabel.append(0)
            '-------------------------------------------------'
            f1 = computeFScore(truelabel, predlabel)
        else:####只有一个查询节点，说明只有ego直接返回1
            f1=1

        allF1Scores.append(f1)
        # allPrecision.append(precision)
        # allRecall.append(recall)
    # print allF1Scores
    # print len(allF1Scores)
    if len(allF1Scores) != 0:
        avrgf1 = sum(allF1Scores) / float(len(allF1Scores))
    else:
        avrgf1 = 0
    # avrgprecision=sum(allPrecision)/float(len(allPrecision))
    # avrgrecall=sum(allRecall)/float(len(allRecall))
    maxf1=0
    minf1=0
    if len(allF1Scores)>0:
        maxf1= max(allF1Scores)
        minf1= min(allF1Scores)
    # print avrgprecision
    # print avrgrecall
    return avrgf1,minf1,maxf1




def printallIncF1s(allavF1,allminF1,allmaxF1,dataList,alphaList):
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


def runF1Inc():
    '普通的数据集'
    dataList=['citeseer','cora','cornell','texas','wisconsin','washington']
    dataList2=['citeseer','cora']
    alphaList=[0,2,4,6,8,10]
    alphaList2=[0,1,2,3,4,5,6,7,8,9,10]
    allavF1={}
    allminF1={}
    allmaxF1={}
    for data in dataList2:
        allavF1[data]={}
        allminF1[data]={}
        allmaxF1[data]={}
        for alpha in alphaList2:
            avF1,minF1,maxF1=computeF1Inc(data,10,alpha)
            allavF1[data][alpha]=avF1
            allminF1[data][alpha]=minF1
            allmaxF1[data][alpha]=maxF1

    '按F1分类打印'
    printallIncF1s(allavF1, allminF1, allmaxF1, dataList2, alphaList2)

def runF1IncFB():
    'facebook的'
    egoList=[0,107,348,414,686,698,1684,1912,3437,3980]
    egoList2=[1912,3437,3980]
    'csm+Inc'
    alphaList = [0, 2, 4, 6, 8, 10]
    allavF1={}
    allminF1={}
    allmaxF1={}
    for data in egoList:
        allavF1[data]={}
        allminF1[data]={}
        allmaxF1[data]={}
        for alpha in alphaList:
            avF1,minF1,maxF1=egoNetworkIncF1(data,alpha,10)
            allavF1[data][alpha]=avF1
            allminF1[data][alpha]=minF1
            allmaxF1[data][alpha]=maxF1

    '按F1分类打印'
    printallIncF1s(allavF1, allminF1, allmaxF1, egoList, alphaList)
    # 'cst'
    # kList=[1,2,4,8,16,32]
    # for ego in egoList:
    #     for k in kList:
    #         print "****************************"
    #         print 'ego: ',ego,' k= ',k
    #         egoNetworkF1(ego,k)

def runF1DecFB():
    'facebook的'
    egoList=[0,107,348,414,686,698,1684,1912,3437,3980]

    'csm+Inc'
    allavF1={}
    allminF1={}
    allmaxF1={}
    for data in egoList:
        avF1,minF1,maxF1=egoNetworkF1Dec(data,10)
        allavF1[data]=avF1
        allminF1[data]=minF1
        allmaxF1[data]=maxF1

        '打印总分'
    print 'data\tmin\t\ave\tmax'
    for ego in egoList:
        print str(ego),'\t',allminF1[ego],'\t',allavF1[ego],'\t',allmaxF1[ego]

def runF1Dec():
    dataList = ['citeseer', 'cora', 'cornell', 'texas', 'wisconsin', 'washington']
    dataList2=['dblps']
    allavF1={}
    allminF1={}
    allmaxF1={}
    for data in dataList2:
        avF1, minF1, maxF1 = computeF1Dec(data,1)
        allavF1[data]= avF1
        allminF1[data] = minF1
        allmaxF1[data] = maxF1

    '打印总分'
    print 'data\tmin\t\ave\tmax'
    for data in dataList:
        print data,'\t',allminF1[data],'\t',allavF1[data],'\t',allmaxF1[data]

if __name__=='__main__':
    # runF1Dec()
    # runF1DecFB()
    runF1Inc()
    # runF1IncFB()
