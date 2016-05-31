import re
from flask import render_template
from flask import request
from movie_home import app
from movie_home.models import mtime


@app.route('/')
@app.route('/index')
def index():
    movies = mtime.objects.all()
    return render_template("index.html", movies=movies)

@app.route('/search', methods=['POST', ])
def search():
    keyword = request.form.get("keyword")
    print keyword
    movies = mtime.objects(__raw__ = {"movie_name":re.compile("^.*?" + keyword + ".*?")})
    return render_template("search_result.html", movies=movies)
