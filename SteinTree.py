# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:SteinTree.py
@time:2017/3/611:14
@Function：计算包含查询节点的最小生成树
"""
import networkx as nx
import copy

def buildSteinerTree(queryVertexes,G):
    '假设只包含一个节点的话直接返回'
    if (len(queryVertexes)==1):
         return G.subgraph(queryVertexes)
    '多个查询节点的情况'
    '1:计算每个查询节点到其他查询节点的最短路径'
    shortestLength=nx.all_pairs_shortest_path_length(G) ###计算皆有节点对知己恩的最短路径
    shortestPath=nx.all_pairs_shortest_path(G) ##计算最短路径
    '2:构造只有查询节点，边权重是最短路径长度的完全图G1'
    weightedG=nx.Graph()
    for V1 in queryVertexes:
        for V2 in queryVertexes:
            weightedG.add_edge(V1,V2,weight=shortestLength[V1][V2])
    '3:在上一步的G1中构造最小生成树G2'
    G2=nx.minimum_spanning_tree(weightedG)
    '4：将原图G2的边替换成G2两节点之间的最短路径，构建G的子图G3'
    G3=nx.Graph()
    for edge in G2.edges_iter():
        path=shortestPath[edge[0]][edge[1]]
        for v in path:
            if not G3.has_node(v):
                G3.add_node(v)
                for nei in G.neighbors(v):
                    if G3.has_node(nei):
                        G3.add_edge(v,nei)
    ##EECS到这里就结束了
    # return G3
    print 'G3:',G3.nodes()

    '5:在G3找最小生成树G4'
    G4=nx.minimum_spanning_tree(G3)
    print 'G4:',G4.nodes()
    '6:Construct a ST tree G5 from G4 by deleting edges in G4,' \
    'if necessary,so that no leaves in G5 are ST vertices'
    return G4


if __name__=='__main__':
    G=nx.read_adjlist('Data/toyTruess-graph',nodetype=int)
    query=[6,9,2]
    res=buildSteinerTree(query,G)

