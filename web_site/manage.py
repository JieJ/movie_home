# -*- coding: utf-8 -*-

from flask.ext.script import Manager, Server
from movie_home import app
from movie_home.models import mtime

manager = Manager(app)

manager.add_command("runserver",
         Server(host='localhost',port=5000, use_debugger=True))

if __name__ == '__main__':
    manager.run()
