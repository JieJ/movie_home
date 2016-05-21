# -*- coding: utf-8 -*-
"""
定义数据库链接
"""
# import settings.py
from pymongo import MongoClient

class ys66_db(object):
    server = 'localhost'
    port = 27017
    client = MongoClient(server, port)
    db = client['movie_home']
    collection = db['ys66']

    @classmethod
    def insert_one_record(self, item):
        try:
            self.collection.insert_one(item)
        except:
            print "##"

class mtime_db(object):
    server = 'localhost'
    port = 27017
    client = MongoClient(server, port)
    db = client['movie_home']
    collection = db['mtime']

    @classmethod
    def insert_one_record(self, item):
        try:
            self.collection.insert_one(item)
        except:
            print "##"
