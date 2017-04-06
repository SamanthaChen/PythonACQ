# -*- coding:utf-8 -*-
"""
@author:SamanthaChen
@file:PriprityQueue.py
@time:2017/3/2120:45
"""
'利用最小堆实现一个优先队列，值大的优先级高'
from heapq import heappush, heappop


class PriorityQueue:
    def __init__(self):
        self._queue = []

    def put(self, item, priority):
        heappush(self._queue, (-priority, item))

    def get(self):
        return heappop(self._queue)[-1]


    def __str__(self):
        return str(self._queue)


if __name__=='__main__':
    q = PriorityQueue()
    q.put('world', 1)
    q.put('hello', 2)
    q.put('a',3)

    print 'q:',q
    print 'pop:',q.get()
    print 'q:',q
    q.put('b',5)
    print 'q:',q
    print 'pop:',q.get()