# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:TestMainV2.py
@time:2017/3/3022:05

"""
from OnlineProcessingV2 import *
import time

def runcsmGrD(dataset):
    ###############################################################################
    ####      读query文件，并将结果输出（注意结果文件与query文件相对应）###########
    ###############################################################################
    path='L:/ACQData/'
    # dataset='washington'
    algo='greedyDecV2/'
    edgefile=path+'groundTruthData/'+dataset+'/'+dataset+'_graph'
    labelfile=path+'groundTruthData/'+dataset+'/'+dataset+'_nodelabel'
    queryfile=path+'groundTruthData/'+dataset+'/'+dataset+'_query_1Nei_w3_10'
    outfile=path+algo+dataset+'_query_1Nei_w3_10_csm_res.txt'
    queryVertexes=[] ##包含所有的查询节点
    queryAtts=[] ###包含所有的查询属性
    fq=open(queryfile,'r')
    lineCount=0
    for line in fq.readlines():
        lineCount+=1
        line=line.strip("\n") #把末尾换行符去掉
        words=line.split('\t')

        nodeStartid=words.index('node:')  ####查询节点开始的位置
        attrsStartid=words.index('attr:') ####查询属性开始的位置

        tmp=words[nodeStartid+1:attrsStartid]
        if(len(tmp)==0):  #####可能会出现查询节点为空
            break
        nodeList=[]
        for val in tmp:
            if val:
                nodeList.append(int(val))
        queryVertexes.append(nodeList)

        attrList=words[attrsStartid+1:] ###选择所以关键词
        attrList[-1].strip('\n')  ##去不掉最后一个换行符。。
        queryAtts.append(attrList)

    fq.close()


    print 'Reading graph...'
    G=dataReader3(edgefile,labelfile)

    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root=shellIndex.root
    # #打印树
    # print 'Index Tree:'
    # displayTree(root,0)


    wf=open(outfile,'w')
    for i in range(lineCount):
        print '**************************************************************************'
        print 'NO.'+str(i)+' querying...'
        qnode=queryVertexes[i]
        qattr=queryAtts[i]
        print 'retrieveCSM...'
        resnodes,H,maxCoreness =retrieveCSMV2(qnode,shellIndex)
        if resnodes == None:  ##这个查询条件不能满足了，找别的查询条件
            print "This require k is too big."
            wf.write('No answer.\n')
            continue
        print 'csm:',H.nodes()
        print 'maxCoreness:',maxCoreness
        Hi=greedyDecV2(H,maxCoreness,qnode,qattr)
        # print 'final res:',Hi.nodes()
        ####文件输出
        string=''
        for node in Hi.nodes():
            string+=str(node)+' ' ####空格分割
        wf.write(string+'\n')
        print '**************************************************************************'
    wf.close()

def runcsmGrDFB(ego,attrNum):
    ###############################################################################
    ####      读query文件，并将结果输出（注意结果文件与query文件相对应）###########
    ###############################################################################
    path='L:/ACQData/'
    dataset='facebook'
    algo='greedyDecV2/Times/'
    edgefile=path+'groundTruthData/'+dataset+'/'+dataset+'_ego'+str(ego)+'_graph'
    labelfile=path+'groundTruthData/'+dataset+'/'+dataset+'_ego'+str(ego)+'_nodelabel'
    queryfile=path+'groundTruthData/'+dataset+'/Times/'+dataset+'_ego'+str(ego)+'_query_core3_w'+str(attrNum)+'_10'
    outfile=path+algo+dataset+'_ego'+str(ego)+'_query_core3_w'+str(attrNum)+'_10_csm_res.txt'
    timesfile=path+algo+dataset+'_ego'+str(ego)+'_query_core3_w'+str(attrNum)+'_10_csm_.times'
    queryVertexes=[] ##包含所有的查询节点
    queryAtts=[] ###包含所有的查询属性
    fq=open(queryfile,'r')
    lineCount=0
    coreList=[] ##
    for line in fq.readlines():
        lineCount+=1
        line=line.strip("\n") #把末尾换行符去掉
        words=line.split('\t')

        coreList.append(int(words[1]))  ##核值
        nodeStartid=words.index('node:')  ####查询节点开始的位置
        attrsStartid=words.index('attr:') ####查询属性开始的位置

        tmp=words[nodeStartid+1:attrsStartid]
        if(len(tmp)==0):  #####可能会出现查询节点为空
            break
        nodeList=[]
        for val in tmp:
            if val:
                nodeList.append(int(val))
        queryVertexes.append(nodeList)

        attrList=words[attrsStartid+1:] ###选择所以关键词
        attrList[-1].strip('\n')  ##去不掉最后一个换行符。。
        queryAtts.append(attrList)

    fq.close()

    '存时间的'
    csmtimesList=[[0.0 for col in range(6)] for row in range(10)]
    dectimesList = [[0.0 for col in range(6)] for row in range(10)]


    print 'Reading graph...'
    G=dataReader3(edgefile,labelfile)

    indexStart=time.clock() #开始时间
    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    indexEnd=time.clock() #结束时间
    print '建立索引时间(s)：',indexEnd-indexStart
    root=shellIndex.root
    # #打印树
    # print 'Index Tree:'
    # displayTree(root,0)



    wf=open(outfile,'w')
    for i in range(lineCount):
        print '**************************************************************************'
        print 'NO.'+str(i)+' querying...'
        qnode=queryVertexes[i]
        qattr=queryAtts[i]
        print '|core|=',coreList[i],'|Vq|=',len(qnode),' |Wq|=',len(qattr)
        print 'retrieveCSM...'
        csmStart=time.clock()
        resnodes,H,maxCoreness =retrieveCSMV2(qnode,shellIndex)
        csmEnd=time.clock()
        print 'csm时间(s):',csmEnd-csmStart
        csmtime=csmEnd-csmStart
        csmtimesList[i/6][i%6]=csmtime


        if resnodes == None:  ##这个查询条件不能满足了，找别的查询条件
            print "This require k is too big."
            wf.write('No answer.\n')
            continue
        # print 'csm:',H.nodes()
        print 'maxCoreness:',maxCoreness
        decStart=time.clock()
        Hi=greedyDecV2(H,maxCoreness,qnode,qattr)
        decEnd=time.clock()
        print 'Dec时间（s）:',decEnd-decStart
        dectime=decEnd-decStart
        dectimesList[i/6][i%6]=dectime

        # print 'final res:',Hi.nodes()
        ####文件输出
        string=''
        for node in Hi.nodes():
            string+=str(node)+' ' ####空格分割
        wf.write(string+'\n')
        print '**************************************************************************'
    wf.close()

    '输出时间文件'
    tw=open(timesfile,'w')
    tw.write('csm times:'+'\n')
    for row in range(10):
        line=''
        for col in range(6):
            line+=str(csmtimesList[row][col])+'\t'
        tw.write(line+'\n')

    tw.write('dec times:' + '\n')
    for row in range(10):
        line=''
        for col in range(6):
            line+=str(dectimesList[row][col])+'\t'
        tw.write(line+'\n')

    tw.close()



import time
if __name__=='__main__':

    # dataList=['citeseer','cora','cornell','texas','wisconsin','washington']
    # for data in dataList:
    #     print '【【【【【【【',data,'】】】】】】'
    #     runcsmGrD(data)

    egoList = [0, 107, 348, 414, 686, 698, 1684, 1912, 3437, 3980]
    egoList2=[107,1912]
    egoList3=[1684]
    wqList=[1,2,3,4,5,6,7,8,9,10]
    wqList3=[1]
    for attrNum in wqList:
        for ego in egoList3:
            print '【【【【【【【facebook_ego', str(ego), '|Wq|=',attrNum,'】】】】】】'
            runcsmGrDFB(ego,attrNum)
