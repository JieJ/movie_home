# -*- coding: utf-8 -*-
import os
from app import app


# <html>
#   <head>
#     <title>Home Page</title>
#   </head>
#   <body>
#     <h1>Hello, ''' + user['nickname'] + '''</h1>
#   </body>
# </html>

if __name__ == '__main__':
    app.run(debug=True)
