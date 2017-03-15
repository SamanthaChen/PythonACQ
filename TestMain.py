# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:TestMain.py
@time:2017/3/1215:56
@Function:整个算法的测试程序
"""
from OnlineProcessingV2 import *

def runcsmGrD():
    ###############################################################################
    ####      读query文件，并将结果输出（注意结果文件与query文件相对应）###########
    ###############################################################################
    path='L:/ACQData/'
    dataset='washington'
    algo='greedyDecV2/'
    edgefile=path+'groundTruthData/'+dataset+'/'+dataset+'_graph'
    labelfile=path+'groundTruthData/'+dataset+'/'+dataset+'_nodelabel'
    queryfile=path+'groundTruthData/'+dataset+'/'+dataset+'_query_2Nei_w3_100'
    outfile=path+algo+dataset+'_query_2Nei_w3_100_csm_res.txt'
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
        print 'final res:',Hi.nodes()
        ####文件输出
        string=''
        for node in Hi.nodes():
            string+=str(node)+' ' ####空格分割
        wf.write(string+'\n')
        print '**************************************************************************'
    wf.close()


def runcstGrd():
    ###############################################################################
    ####      读query文件，并将结果输出（注意结果文件与query文件相对应）###########
    ###############################################################################
    path = 'L:/ACQData/'
    dataset = 'citeseer'
    algo = 'greedyDecV2/'
    k = 5
    edgefile = path + 'groundTruthData/' + dataset + '/' + dataset + '_graph'
    labelfile = path + 'groundTruthData/' + dataset + '/' + dataset + '_nodelabel'
    queryfile = path + 'groundTruthData/' + dataset + '/' + dataset  +'_query_2Nei_w3_100'
    outfile = path + algo + dataset + '_query_2Nei_w3_100_k' + str(k) + '_res.txt'
    queryVertexes = []  ##包含所有的查询节点
    queryAtts = []  ###包含所有的查询属性

    fq = open(queryfile, 'r')
    lineCount = 0
    for line in fq.readlines():
        lineCount += 1
        line = line.strip("\n")  # 把末尾换行符去掉
        words = line.split('\t')

        nodeStartid = words.index('node:')  ####查询节点开始的位置
        attrsStartid = words.index('attr:')  ####查询属性开始的位置

        tmp = words[nodeStartid + 1:attrsStartid]
        if (len(tmp) == 0):  #####可能会出现查询节点为空
            break
        nodeList = []
        for val in tmp:
            if val:
                nodeList.append(int(val))
        queryVertexes.append(nodeList)

        attrList = words[attrsStartid + 1:]  ###选择所以关键词
        attrList[-1].strip('\n')  ##去不掉最后一个换行符。。
        queryAtts.append(attrList)

    fq.close()

    print 'Reading graph...'
    G = dataReader3(edgefile, labelfile)

    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root = shellIndex.root
    # #打印树
    # print 'Index Tree:'
    # displayTree(root,0)


    wf = open(outfile, 'w')
    for i in range(lineCount):
        print '**************************************************************************'
        print 'NO.' + str(i) + ' querying...'
        qnode = queryVertexes[i]
        qattr = queryAtts[i]
        print 'retrieveCST,k=', str(k), '...'

        resVertexew, H, maxCoreness = retrieveCSTV2(qnode, shellIndex,k)
        if resVertexew==None: ##这个查询条件不能满足了，找别的查询条件
            print "This require k is too big."
            wf.write( 'No answer.\n')
            continue

        print 'cst:', H.nodes()
        Hi= greedyDecV2(H, k, qnode, qattr)

        print 'final res:', Hi.nodes()
        ####文件输出
        string = ''
        for node in Hi.nodes():
            string += str(node) + ' '  ####空格分割
        wf.write(string + '\n')
        print '**************************************************************************'
    wf.close()


if __name__=='__main__':
    # runcstGrd()
    runcsmGrD()