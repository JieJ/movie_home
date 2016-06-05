import re
from flask import render_template
from flask import request
from movie_home import app
from movie_home.models import mtime, ys66


@app.route('/')
@app.route('/index2')
def index():
    # movies = mtime.objects.all()
    # return render_template("index.html", movies=movies)
    return render_template("index2.html")


@app.route('/index')
def index2():
    # movies = mtime.objects.all()
    # return render_template("index.html", movies=movies)
    return render_template("index.html")

@app.route('/search', methods=['POST', ])
def search():
    keyword = request.form.get("keyword")
    print keyword
    # movies = mtime.objects(__raw__ = {"movie_name":re.compile("^.*?" + keyword + ".*?")})
    movies = ys66.objects(__raw__ = {"movie_name":re.compile("^.*?" + keyword + ".*?")})
    return render_template("search_result2.html", movies=movies)
