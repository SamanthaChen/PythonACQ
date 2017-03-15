# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:TextDealer.py
@time:2017/3/219:42
"""
from  collections import defaultdict
#######删除文件中重复的行
def deleteDupLine():
    '#删除文件中重复的行'
    rFile = open("Data/user_tag.dat", "r")
    wFile = open("Data/user_tag2.dat", "w")
    allLine = rFile.readlines()
    rFile.close()
    h = {}
    for i in allLine:
        if not h.has_key(i):
            h[i]=1
            wFile.write(i)
    wFile.close()

####将节点映射成从1开始
def convertStyle():
    ####将邻接表格式改成一行两个点的格式
    rFile = open("Data/lastfm_graph", "r")
    wFile = open("DataNew/lastfm_all.edges", "w")
    ###读文件
    d=defaultdict(list)
    for line in rFile.readlines():
        words=line.split()
        d[words[0]]=words[1:]
    rFile.close()
    ###写文件
    for key,value in d.items():
        for v in value:
            s=''+key+'\t'+v
            wFile.write(s+'\n')
    wFile.close()


def convertStyle2():
    ####将邻接表格式改成一行两个点的格式
    data = 'cora'
    rFile = open('L:/ACQData/groundTruthData/' + data + '/' + data + '_nodelabel', "r")
    wFile = open("L:/ACQData/LDense/"+data+"_all.featlabels", "w")
    ###读文件
    d=defaultdict(list)
    for line in rFile.readlines():
        words=line.split()
        d[words[0]]=words[1:]
    rFile.close()
    ###写文件
    for key,value in d.items():
        for v in value:
            s=''+key+' '+v  #####空格分割
            wFile.write(s+'\n')
    wFile.close()

def info2onlyNode():
    ###################将包含core信息和属性信息的文件转换为只有查询节点的文件
    rFile = open("L:/ACQData/lastfm_Query_wall.txt", "r")
    wFile = open("L:/ACQData/lastfm_Query_wall_onlyNode.txt", "w")
    for line in rFile.readlines():
        words=line.split('\t')
        nodeStartid=words.index('node:')  ####查询节点开始的位置
        attrsStartid=words.index('attrs:') ####查询属性开始的位置
        s=''
        for i in words[nodeStartid+1:attrsStartid]:
            s += i+'\t'
        s.strip('\t')
        wFile.write(s+'\n')
    wFile.close()
    rFile.close()

def info2onlyNode2():
    ###################将包含core信息和属性信息的文件转换为只有查询节点的文件
    data='cora'
    rFile = open('L:/ACQData/groundTruthData/'+data+'/'+data+'_query_2Nei_w3_100', "r")
    wFile = open('L:/ACQData/cocktail/'+data+'/'+data+'_query_2Nei_w3_100_onlyNode', "w")
    for line in rFile.readlines():
        words=line.split('\t')
        nodeStartid=words.index('node:')  ####查询节点开始的位置
        attrsStartid=words.index('attr:') ####查询属性开始的位置
        s=''
        for i in words[nodeStartid+1:attrsStartid]:
            s += i+'\t'
        s.strip('\t')
        wFile.write(s+'\n')
    wFile.close()
    rFile.close()

def adj2edge():
    ################将adjList处理成edgeList

    rFile = open("L:\ACQData\cocktail\lastfm_graph", "r")
    wFile = open("L:\ACQData\cocktail\lastfm_edgeList", "w")
    for line in rFile.readlines():
        words=line.split()
        for adj in words[1:]:
            s=''
            s+=words[0]+'\t'+adj
            wFile.write(s+'\n')
    wFile.close()
    rFile.close()

def citseer():
    '处理citeseer类型的数据'
    dataName='WebKB/wisconsin'
    path='L:/ACQData/groundTruthData/'
    citesFile=path+dataName+'.cites'
    contentFile=path+dataName+'.content'
    outputGraphFile=path+dataName+'_graph'
    outputLabelFile=path+dataName+'_nodelabel'
    outputClassFile=path+dataName+'_class'
    outputMapFile=path+dataName+'_idMap'
    idmap={}
    adjDict=defaultdict(list)
    labelDict=defaultdict(list)
    classDict={} ##最终分类
    '1:创建链接表'
    citef=open(citesFile,'r')
    count=0
    for line in citef.readlines():
        line=line.strip()
        words=line.split()
        if not idmap.has_key(words[0]):
            idmap[words[0]]=count
            count+=1
            # print count
        if not idmap.has_key(words[1]):
            idmap[words[1]]=count
            count+=1
            # print count
        ####加入邻接链表
        ###把引用自己的情况忽略
        u=idmap[words[0]]
        v=idmap[words[1]]
        if u==v:
            continue
        adjDict[u].append(v)
        adjDict[v].append(u)
    citef.close()

    '1.1：写边文件'
    graphw=open(outputGraphFile,'w')
    for key,value in adjDict.items():
        s=str(key)
        for nei in value:
            s+=' '+str(nei)
        graphw.write(s+'\n')
    graphw.close()
    '2. 读节点文件和社团文件'
    contentf=open(contentFile,'r')
    for line in contentf.readlines():
        line=line.strip()
        words=line.split()
        id=idmap[words[0]]
        rawAttr=[int(val) for val in words[1:-1]]
        classid=words[-1]
        ###处理属性
        for i in range(len(rawAttr)):
            if rawAttr[i]==1:
                labelDict[id].append(i)
        ####处理class标签
        classDict[id]=classid
    '3.写属性文件'
    attw=open(outputLabelFile,'w')
    for key,value in labelDict.items():
        s=str(key)
        for a in value:
            s+=' '+str(a)
        attw.write(s+'\n')
    attw.close()
    '4.写class文件'
    classw=open(outputClassFile,'w')
    for key,value in classDict.items():
        s=str(key)+' '+value
        classw.write(s+'\n')
    '5.写map文件'
    mapw=open(outputMapFile,'w')
    for k,v in idmap.items():
        s=k+' '+str(v)
        mapw.write(s+'\n')
    mapw.close()



def deletNei():
    rFile=open('E:\ACQ\Datasets\citeseer_graph','r')
    wFile=open('E:\ACQ\Datasets\citeseer_graph_true','w')
    allLine = rFile.readlines()
    rFile.close()
    for line in allLine:
        line=line.strip()
        words=line.split()
        newwords=[]
        ###找标号小于3327的节点
        for si in words:
            if int(si)<3279:
                newwords.append(si)
        ##写文件
        newline=''
        for j in newwords:
            newline+=j+' '
        newline=newline.strip()
        wFile.write(newline+'\n')
    wFile.close()



def add0dNode():
    path='L:/ACQData/groundTruthData/'
    dataName='wisconsin'
    rFile=open(path+dataName+'/'+dataName+'_graph','r')
    wFile=open(path+dataName+'/'+dataName+'_graph_all','w')
    allLine = rFile.readlines()
    rFile.close()

    ###统计原来度>0的节点
    oldSet=set()
    maxid=0
    for line in allLine:
        words=line.split()
        id=int(words[0])
        oldSet.add(id)
        if id>maxid:
            maxid=id
    ###找度等于0的节点
    zeroNode=[]
    for i in range(maxid+1):
        if i not in oldSet:
            zeroNode.append(i)
    ###重新输出文件
    for line in allLine:
        wFile.write(line)
    for n in zeroNode:
        wFile.write(str(n)+'\n')
    wFile.close()



if __name__=='__main__':
    # add0dNode()
    info2onlyNode2()
    # convertStyle2()