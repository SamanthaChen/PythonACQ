# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:TestMainIncV2.py
@time:2017/3/3022:20
"""
from OnlineProcessingV2 import *


def runcsmGrInc(dataset,alpha):
    ###############################################################################
    ####      读query文件，并将结果输出（注意结果文件与query文件相对应）###########
    ###############################################################################
    path='L:/ACQData/'
    # dataset='citeseer'
    algo='greedyInc/'
    # alpha=1 ###调和属性与结构,alpha越大，结构分数越大
    edgefile=path+'groundTruthData/'+dataset+'/'+dataset+'_graph'
    labelfile=path+'groundTruthData/'+dataset+'/'+dataset+'_nodelabel'
    queryfile=path+'groundTruthData/'+dataset+'/'+dataset+'_query_2Nei_w3_test'
    outfile=path+algo+dataset+'_query_2Nei_w3_test_csm_res_a'+str(int(alpha*10))+'.txt'
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
        # print 'csm:',H.nodes()
        print 'len(csm):',len(H)
        print 'maxCoreness:',maxCoreness
        '在线查询的算法'
        print 'greedyInc ...'
        Hi=greedyIncFromH(G,H,maxCoreness,qnode,qattr,alpha)  ####（re：2017.3.15,候选范围从H扩大到H# ）
        print 'len(res)：',len(Hi)
        # print 'final res:',Hi.nodes()
        ####文件输出
        string=''
        for node in Hi.nodes():
            string+=str(node)+' ' ####空格分割
        wf.write(string+'\n')
        print '**************************************************************************'
    wf.close()


def runcsmGrIncFB(ego,dataset,alpha,attrNum):
    '''

    :param ego:
    :param dataset:
    :param alpha:
    :return:
    '''
    ###############################################################################
    ####      读query文件，并将结果输出（注意结果文件与query文件相对应）###########
    ###############################################################################
    path='L:/ACQData/'
    # dataset='cora'
    algo='greedyInc/Times/'
    # alpha=0.5 ###调和属性与结构,alpha越大，结构分数越大
    edgefile=path+'groundTruthData/'+dataset+'/'+dataset+'_ego'+str(ego)+'_graph'
    labelfile=path+'groundTruthData/'+dataset+'/'+dataset+'_ego'+str(ego)+'_nodelabel'
    queryfile=path+'groundTruthData/'+dataset+'/Times/'+dataset+'_ego'+str(ego)+'_query_core3_w'+str(attrNum)+'_10'
    outfile=path+algo+dataset+'_ego'+str(ego)+'_query_core_w'+str(attrNum)+'_10_csm_res_a'+str(int(alpha*10))+'.txt'
    timesfile = path + algo + dataset + '_ego' + str(ego) + '_query_core3_w' + str(attrNum) + '_10_csm_a'+str(int(alpha*10))+'.times'
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

    '存时间的'
    csmtimesList = [[0.0 for col in range(6)] for row in range(10)]
    dectimesList = [[0.0 for col in range(6)] for row in range(10)]

    print 'Reading graph...'
    G=dataReader3(edgefile,labelfile)

    print 'Index building...'
    indexStart = time.clock()  # 开始时间
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
        print 'retrieveCSM...'
        csmStart = time.clock()
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
        print 'len(csm):',len(H)
        print 'maxCoreness:',maxCoreness
        '在线查询的算法'
        print 'greedyInc ...'
        incStart = time.clock()
        Hi=greedyIncFromH(G,H,maxCoreness,qnode,qattr,alpha)  ####（re：2017.3.20,候选范围H# ）
        incEnd = time.clock()
        print 'Inc时间（s）:',incEnd-incStart
        dectime=incEnd-incStart
        dectimesList[i/6][i%6]=dectime
        # print 'len(res)：',len(Hi)
        # print 'final res:',Hi.nodes()
        ####文件输出
        string=''
        for node in Hi.nodes():
            string+=str(node)+' ' ####空格分割
        wf.write(string+'\n')
        print '**************************************************************************'
    wf.close()

    '输出时间文件'
    tw = open(timesfile, 'w')
    tw.write('csm times:' + '\n')
    for row in range(10):
        line = ''
        for col in range(6):
            line += str(csmtimesList[row][col]) + '\t'
        tw.write(line + '\n')

    tw.write('inc times:' + '\n')
    for row in range(10):
        line = ''
        for col in range(6):
            line += str(dectimesList[row][col]) + '\t'
        tw.write(line + '\n')

    tw.close()


import time
if __name__=='__main__':
    '普通的数据集'
    # dataList=['cora','cornell','texas','wisconsin','washington','citeseer']
    # dataList2=['imdb']
    # dataList3=['cora','citeseer']
    # alphaList=[0.0,0.2,0.4,0.6,0.8,1.0]
    # alphaList2 = [ 0.5]
    # alphaList3=[0.0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1.0]
    # 'csm'
    # for dataset in dataList3:
    #     # print '#############################################################'
    #     print  '#######################   ',dataset,'  #########################'
    #     # print '#############################################################'
    #     for alpha in alphaList2:
    #         print '--------------alpha=',alpha,'-----------'
    #         runcsmGrInc(dataset,alpha)
    'cst'

    'facebook的数据集'
    'csm'
    egoList=[0,107,348,414,686,698,1684,1912,3437,3980]
    egoList2=[107,1912]
    egoList3=[414]
    alphaList2 = [0.5]
    wqList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    wqList3=[1]
    for attrNum in wqList:
        for ego in egoList3:
            # print '#############################################################'
            print  '#######################   facebook',ego,'  #########################'
            # print '#############################################################'
            for alpha in alphaList2:
                runcsmGrIncFB(ego,'facebook',alpha,attrNum)