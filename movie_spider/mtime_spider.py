# -*- coding: utf-8 -*-
"""
时光网爬虫
"""
import requests
import os
import re
from datetime import datetime

if __name__ == '__main__':

    start = datetime.now()

    url = 'http://service.channel.mtime.com/service/search.mcs'
    data = {
        'Ajax_CallBack' : 'true',
        'Ajax_CallBackType' : 'Mtime.Channel.Pages.SearchService',
        'Ajax_CallBackMethod' : 'SearchMovieByCategory',
        'Ajax_CrossDomain' : 1,
        'Ajax_RequestUrl' : 'http://movie.mtime.com/movie/search/section/#year=2000',
        't' : '201651216485391989',
        'Ajax_CallBackArgument9' : 2000,
        'Ajax_CallBackArgument10' : 2000,
        'Ajax_CallBackArgument11' : 0,
        'Ajax_CallBackArgument12' : 0,
        'Ajax_CallBackArgument13' : 0,
        'Ajax_CallBackArgument14' : 1,
        'Ajax_CallBackArgument15' : 0,
        'Ajax_CallBackArgument16' : 1,
        'Ajax_CallBackArgument17' : 4,
        'Ajax_CallBackArgument18' : 4,
        'Ajax_CallBackArgument19' : 0,
    }

    # url = 'http://service.channel.mtime.com/service/search.mcs'
    # data = {
    #     'Ajax_CallBack' : 'true',
    #     'Ajax_CallBackType' : 'Mtime.Channel.Pages.SearchService',
    #     'Ajax_CallBackMethod' : 'SearchMovieByCategory',
    #     'Ajax_CrossDomain' : 1,
    #     'Ajax_RequestUrl' : 'http://movie.mtime.com/movie/search/section/#year=2000',
    #     't' : '201651216485391989',
    #     'Ajax_CallBackArgument0' : '',
    #     'Ajax_CallBackArgument1' : 0,
    #     'Ajax_CallBackArgument2' : 0,
    #     'Ajax_CallBackArgument3' : 0,
    #     'Ajax_CallBackArgument4' : 0,
    #     'Ajax_CallBackArgument5' : 0,
    #     'Ajax_CallBackArgument6' : 0,
    #     'Ajax_CallBackArgument7' : 0,
    #     'Ajax_CallBackArgument8' : '',
    #     'Ajax_CallBackArgument9' : 2000,
    #     'Ajax_CallBackArgument10' : 2000,
    #     'Ajax_CallBackArgument11' : 0,
    #     'Ajax_CallBackArgument12' : 0,
    #     'Ajax_CallBackArgument13' : 0,
    #     'Ajax_CallBackArgument14' : 1,
    #     'Ajax_CallBackArgument15' : 0,
    #     'Ajax_CallBackArgument16' : 1,
    #     'Ajax_CallBackArgument17' : 4,
    #     'Ajax_CallBackArgument18' : 2,
    #     'Ajax_CallBackArgument19' : 0,
    # }

    r = requests.get(url, params=data)
    with open('content.txt', 'w') as xs:
        xs.write(r.content)



    end = datetime.now()

    print u"耗时：", end - start

