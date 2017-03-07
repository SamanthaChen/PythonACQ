# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:LDenseDealer.py
@time:2017/3/516:15
"""

####处理LDense的
###4的倍数行存的是社团
def raw2Community():
    rFile=open('L:\ACQData\LDense\delicious\delicious_all_A.lo_100.communities','r')
    wFile=open('L:\ACQData\LDense\delicious\delicious_100','w')
    lineNum=1
    for line in rFile.readlines():
        if(lineNum%4==0):
            line=line.replace(' (','')
            line=line.replace(',','')
            line=line.replace(')','')
            line.strip()
            wFile.write(line)
        lineNum+=1

if __name__=='__main__':
    raw2Community()