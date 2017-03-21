# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:TestMainInc.py
@time:2017/3/1513:23
@Function ：greedyInc的尝试
"""
from OnlineProcessingV2 import *

def runcsmGrInc():
    ###############################################################################
    ####      读query文件，并将结果输出（注意结果文件与query文件相对应）###########
    ###############################################################################
    path='L:/ACQData/'
    dataset='citeseer'
    algo='greedyInc/'
    alpha=1 ###调和属性与结构,alpha越大，结构分数越大
    edgefile=path+'groundTruthData/'+dataset+'/'+dataset+'_graph'
    labelfile=path+'groundTruthData/'+dataset+'/'+dataset+'_nodelabel'
    queryfile=path+'groundTruthData/'+dataset+'/'+dataset+'_query_2Nei_w3_100'
    outfile=path+algo+dataset+'_query_2Nei_w3_100_csm_res_a'+str(int(alpha*10))+'.txt'
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
        Hi=greedyInc(G,H,maxCoreness,qnode,qattr,alpha)  ####（re：2017.3.15,候选范围从H扩大到G）
        print 'len(res)：',len(Hi)
        # print 'final res:',Hi.nodes()
        ####文件输出
        string=''
        for node in Hi.nodes():
            string+=str(node)+' ' ####空格分割
        wf.write(string+'\n')
        print '**************************************************************************'
    wf.close()


def runcsmGrIncFB(ego,dataset):
    ###############################################################################
    ####      读query文件，并将结果输出（注意结果文件与query文件相对应）###########
    ###############################################################################
    path='L:/ACQData/'
    # dataset='cora'
    algo='greedyInc/'
    alpha=0.5 ###调和属性与结构,alpha越大，结构分数越大
    edgefile=path+'groundTruthData/'+dataset+'/'+dataset+'_ego'+str(ego)+'_graph'
    labelfile=path+'groundTruthData/'+dataset+'/'+dataset+'_ego'+str(ego)+'_nodelabel'
    queryfile=path+'groundTruthData/'+dataset+'/'+dataset+'_ego'+str(ego)+'_query_1Nei_w3_10'
    outfile=path+algo+dataset+'_ego'+str(ego)+'_query_2Nei_w3_100_csm_res_a'+str(int(alpha*10))+'.txt'
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
        Hi=greedyInc(G,H,maxCoreness,qnode,qattr,alpha)  ####（re：2017.3.15,候选范围从H扩大到G）
        print 'len(res)：',len(Hi)
        # print 'final res:',Hi.nodes()
        ####文件输出
        string=''
        for node in Hi.nodes():
            string+=str(node)+' ' ####空格分割
        wf.write(string+'\n')
        print '**************************************************************************'
    wf.close()

if __name__=='__main__':
    runcsmGrInc()
    'csm'
    # egoList=[0,107,348,414,686,698,1684,1912,3437,3980]
    # for ego in egoList:
    #     runcsmGrInc(ego,'facebook')
    'cst'
    # coreList=[1,2,4,8,16,32]
    # for ego in egoList:
    #     for i in coreList:
    #         runcstGrdFB(ego,'facebook',i)