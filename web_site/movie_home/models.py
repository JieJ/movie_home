# -*- coding: utf-8 -*-
from movie_home import db
import datetime

class mtime(db.Document):
    movie_name = db.StringField()
    show_year = db.IntField()
    director = db.StringField()
    starring = db.StringField()
    url = db.StringField()
    comment_counts = db.IntField()

class ys66(db.Document):
    movie_name = db.StringField()
    movie_url = db.StringField()
    movie_type = db.StringField()
    download_info = db.ListField()
    wangpan_info = db.ListField()
