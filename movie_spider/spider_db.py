# -*- coding: utf-8 -*-
"""
定义数据库链接与操作
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
    collection = db['mtime_movie_2016']

    
    @classmethod
    def find_one_record(self, filter):
        try:
            res = self.collection.find_one(filter)
            return res
        except:
            print "##"
            return None

    @classmethod
    def insert_one_record(self, item):
        try:
            self.collection.insert_one(item)
        except:
            print "##"
    
    @classmethod
    def update_one_record(self, filter, item, upsert=True):
        try:
            res = self.collection.update_one(filter, item, upsert=upsert)
            print res.matched_count, res.modified_count
        except:
            print "##"


class mtime_db_actor(object):
    server = 'localhost'
    port = 27017
    client = MongoClient(server, port)
    db = client['movie_home']
    collection = db['mtime_actor']

    @classmethod
    def insert_one_record(self, item):
        try:
            self.collection.insert_one(item)
        except:
            print "##"

    @classmethod
    def update_one_record(self, filter, item, upsert=True):
        try:
            res = self.collection.update_one(filter, item, upsert=upsert)
            print res.matched_count, res.modified_count
        except:
            print "##"
    
    # @classmethod
    # def update_one_record(self, filter, item, upsert=True):
    #     try:
    #         res = self.collection.update_one(filter, item, upsert=upsert)
    #         print res.matched_count, res.modified_count
    #     except:
    #         print "##"
        

class mtime_db_director(object):
    server = 'localhost'
    port = 27017
    client = MongoClient(server, port)
    db = client['movie_home']
    collection = db['mtime_director']

    @classmethod
    def insert_one_record(self, item):
        try:
            self.collection.insert_one(item)
        except:
            print "##"
    
    @classmethod
    def update_one_record(self, filter, item, upsert=True):
        try:
            res = self.collection.update_one(filter, item, upsert=upsert)
            print res.matched_count, res.modified_count
        except:
            print "##"
