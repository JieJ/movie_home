# -*- coding: utf-8 -*-
"""
时光网爬虫
"""
import requests
import os
import re
import json
import time
import random
from datetime import datetime

from Queue import Queue
from time import sleep

from bs4 import BeautifulSoup

from spider import spider
from spider_thread import spider_thread
from spider_db import mtime_db

# css selector info
# div class = td pl12 pr20
#     h3 class=normal mt6
#         a href(url) text(movie_name)
#     p class = c_666 mt6 text(评分人数)

# div class = clearfix pt15
#     dl class = info_l
#         dd class = __r_c_
#             a text(导演)

def mtime_spider(thread_id, year_queue, logger_handle, least_comment_num):
    url = 'http://service.channel.mtime.com/service/search.mcs'
    data = {
        'Ajax_CallBack' : 'true',
        'Ajax_CallBackType' : 'Mtime.Channel.Pages.SearchService',
        'Ajax_CallBackMethod' : 'SearchMovieByCategory',
        'Ajax_CrossDomain' : 1,
        'Ajax_RequestUrl' : 'http://movie.mtime.com/movie/search/section/#',
        't' : '201652322134011210',
        # 'Ajax_CallBackArgument9' : 2000,
        # 'Ajax_CallBackArgument10' : 2000,
        'Ajax_CallBackArgument11' : 0,
        'Ajax_CallBackArgument12' : 0,
        'Ajax_CallBackArgument13' : 0,
        'Ajax_CallBackArgument14' : 1,
        'Ajax_CallBackArgument15' : 0,
        'Ajax_CallBackArgument16' : 1,
        'Ajax_CallBackArgument17' : 4,              # sort method 2: 按评分排序 4:按评分人数排序 8: 按年代排序
        # 'Ajax_CallBackArgument18' : 4,              # page index
        'Ajax_CallBackArgument19' : 0,
    }
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    page_stop_flag = 0
    empty_time = 0
    sleep_time = 3
    year = 0
    while True:
        if empty_time > 10 :
            break
        try:
            year = year_queue.get(0)
            print "\n consumed url from Q size now", year_queue.qsize()
            print "size now", year_queue.qsize()
        except:
            sleep(sleep_time)
            empty_time += 1
            continue

        print thread_id, "parsing year", year
        i = 1
        while i < 10000:
            if page_stop_flag == 1:
                i = 10001
                continue
            data['Ajax_CallBackArgument18'] = i;    # page index
            data['Ajax_CallBackArgument9'] = year
            data['Ajax_CallBackArgument10'] = year


            r = requests.get(url, headers=headers, params=data)
            content = re.findall('.*?(\{.*\}).*', r.content)[0]

            # replace_str_1 = 'var result_' + data['t'] + ' = '
            # replace_str_2 = ';var searchMovieByCategoryResultObject=result_'+ data['t'] + ';'
            # content = r.content.replace(replace_str_1, '').replace(replace_str_2, '')


            response_json = {}
            try:
                response_json = json.loads(content)
            except:
                print "error"
                continue

            # print response_json.keys()
            # print response_json['value']['listHTML']

            # 这里使用dom树进行匹配出现了未知错误，匹配不到内容
            # soup = BeautifulSoup(response_json['value']['listHTML'], 'lxml') # making soup
            # movie_namelist, movie_url_list = zip(*[(tag.text, tag['href']) for tag in \
            # soup.select('div[class="td.pl12.pr20"] h3[class="normal.mt6"] a')])
            # 当属性名称中含有空格时，需要用"."代替空格
            # comment_counts_list = [tag.text.replace(u'评分', '') for tag in \
            # soup.select('div[class="td.pl12.pr20"] p[class="c_666.mt6"]')]

            # 改用正则表达式匹配
            html = ''
            if response_json.has_key('value') and response_json['value'].has_key('listHTML'):
                html = response_json['value']['listHTML']
            else:
                logger_handle.write(' '.join(response_json.keys()) + '\n')

            lst = re.findall(u'<h3 class=\"normal mt6\"><a.*?href=\"(.*?)\">(.*?)</a>', html)
            if len(lst) == 0:
                logger_handle.write(str(year) + '\t' + 'page' + str(i) + 'extract movie_name|url error' + '\n')
                continue
            movie_url_list, movie_name_list = zip(*lst)
            comment_counts_list = re.findall(u'<p class=\"c_666 mt6\">(\d*?人评分)</p>', html)

            logger_handle.write(str(len(movie_url_list)) + ' ' + str(len(movie_name_list)) + ' ' + \
                str(len(comment_counts_list)) + '\n')
            # print len(movie_url_list), len(movie_name_list)
            # print len(comment_counts_list)

            if len(movie_url_list) == len(movie_name_list) == len(comment_counts_list):
                for index, text in enumerate(comment_counts_list):
                    if page_stop_flag == 1:
                        break
                    num = int(text.replace(u'人评分', ''))
                    if num >= least_comment_num:
                        movie_name = movie_name_list[index].encode('utf8')
                        detail_url = movie_url_list[index].encode('utf8')
                        detail_r = requests.get(detail_url)

                        director_lst = re.findall('<a.*?rel="v:directedBy">(.*?)</a>', detail_r.content)
                        if len(director_lst) > 0:
                            director = director_lst[0].replace('&#183;', ' ')

                        starring_lst = re.findall('<a.*?rel="v:starring">(.*?)</a>', detail_r.content)
                        if len(starring_lst) > 0:
                            starring = starring_lst[0].replace('·', ' ').replace('&#183;', ' ')

                        print thread_id, movie_name_list[index], num, director.decode('utf8'), year
                        record_item = {
                            'movie_name': movie_name,
                            'show_year': year,
                            'comment_counts': num,
                            'director': director,
                            'starring': starring,
                            'url': detail_url
                        }
                        mtime_db.insert_one_record(record_item)
                    else:
                        print thread_id, u"评分人数少于", least_comment_num, u"不再翻页"
                        page_stop_flag = 1
            i += 1
            sleep(2 + random.uniform(0, 2))


def main(year_lst, thread_num, least_comment_num):
    q = Queue(50)
    for item in year_lst:
        q.put(item, 1)
    # q.put('http://www.66ys.tv/xijupian/index.html', 1)
    # q.put('http://www.66ys.tv/aiqingpian/index.html', 1)
    threads = []
    logger_handle = open('mtime_logger.txt', 'a')
    for i in range(thread_num):
        t = spider_thread(mtime_spider, ('mtime_crawler'+str(i+1), q, logger_handle, least_comment_num), 'crawler'+str(i+1))
        threads.append(t)

    for i in range(thread_num):
        threads[i].start()

    for i in range(thread_num):
        threads[i].join()

    logger_handle.close()


if __name__ == '__main__':

    start = datetime.now()

    year_lst = range(2000, 2002)
    thread_num = 2
    least_comment_num = 200
    main(year_lst, thread_num, least_comment_num)

    end = datetime.now()

    print u"耗时：", end - start























    # full parameters
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
