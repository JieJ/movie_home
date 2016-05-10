# -*- coding: utf-8 -*-
"""
定义一个爬虫线程类，用于多线程爬取
"""
import threading
from time import ctime

class spider_thread(threading.Thread):
    def __init__(self, func, args, name=''):
        threading.Thread.__init__(self)
        self.name = name
        self.func = func
        self.args = args

    def run(self):
        print "start crawler", self.name, 'at', ctime()
        self.func(*self.args)
        print "crawler", self.name, 'finished at', ctime()
