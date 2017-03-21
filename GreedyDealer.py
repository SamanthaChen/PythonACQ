# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:GreedyDealer.py
@time:2017/3/169:57
"""
def testGreedyInc():
    path = 'Data/'
    dataset = 'toy'
    edgefile = path + dataset + '-graph'
    labelfile = path + dataset + '-node'
    queryVertexes = [1, 2, 3]  ##包含所有的查询节点
    queryAtts = ['x', 'y']  ###包含所有的查询属性

    print 'Reading graph...'
    G = dataReader(edgefile, labelfile)

    print 'Index building...'
    shellIndex = ShellIndex(G)
    shellIndex.build()
    root = shellIndex.root
    # #打印树
    # print 'Index Tree:'
    # shellIndex.displayTree(root,0)
    print  'querying...'
    qnodes = queryVertexes
    qattrs = queryAtts

    'CST'
    requireK = 3
    print 'retrieveCST(k=', str(requireK), ')...'
    resnodes, H, maxCoreness = retrieveCSTV2(qnodes, shellIndex, requireK)
    if resnodes == None:
        print "This require k is too big."
        return
    print 'csTNodes:', H.nodes()
    print 'csTEdges:', H.edges()
    print 'maxCoreness:', maxCoreness

    Hi = greedyDecV2(H, requireK, qnodes, qattrs)
    print 'res:', Hi.nodes()