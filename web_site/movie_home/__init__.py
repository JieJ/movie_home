# -*- coding: utf-8 -*-
from flask import Flask
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_object("config")
db = MongoEngine(app)

from movie_home import views, models
