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
