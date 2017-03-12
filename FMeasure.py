# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:FMeasure.py
@time:2017/3/1217:10
"""
from collections import defaultdict

def computeFScore(trueLabels,predLabels):
    '计算两个社团的F1.输入是两个List'
    interSectLen=0.0
    for i in range(len(truelabel)):
        if truelabel[i]==predlabel[i]:
            interSectLen+=1.0

    precision=interSectLen/float(len(predLabels))
    recall=interSectLen/float(len(trueLabels))
    F1Score=(2*precision*recall)/(precision+recall)
    return F1Score

if __name__=='__main__':
    path = 'L:/ACQData/groundTruthData/'
    data = 'citeseer'
    dataName = data + '/' + data
    # edgePath = path + dataName + '_graph'
    classFile = open(path + dataName + '_class', 'r')
    labelFile = open(path + dataName + '_nodelabel', 'r')
    queryTimes=1000
    queryFile = open(path + dataName + '_query_2Nei_w3_'+str(queryTimes), 'r')
    ####算法的结果文件
    resFile=open('L:/ACQData/greedyDecV2/'+data+'_query_2Nei_w3_1000_k3_res.txt','r')
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
        trueclass=nodeClassDict[querysList[id][0]] ###第一个节点的class就是所有查询点的class（因为是在同一个class里面选的查询节点）
        for node in predCom:
            if nodeClassDict[node]==trueclass:
                truelabel.append(1)  ##与查询节点是一类的
            else:
                truelabel.append(0)
            ###预测的标签全都设为一类
            predlabel.append(1)
        f1=computeFScore(truelabel,predlabel)
        allF1Scores.append(f1)
        # allPrecision.append(precision)
        # allRecall.append(recall)
    print allF1Scores
    print len(allF1Scores)
    avrgf1=sum(allF1Scores)/float(len(allF1Scores))
    # avrgprecision=sum(allPrecision)/float(len(allPrecision))
    # avrgrecall=sum(allRecall)/float(len(allRecall))
    print avrgf1
    # print avrgprecision
    # print avrgrecall




