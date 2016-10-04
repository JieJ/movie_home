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

import logging  
logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    filename='movie_spider.log',  
                    filemode='a')

def text_filter(ss):
    return ss.replace('·', '-').replace('&#183;', '-')

def mtime_spider(thread_id, year_queue, least_comment_num):
    url = 'http://service.channel.mtime.com/service/search.mcs'
    data = {
        'Ajax_CallBack' : 'true',
        'Ajax_CallBackType' : 'Mtime.Channel.Pages.SearchService',
        'Ajax_CallBackMethod' : 'SearchMovieByCategory',
        'Ajax_CrossDomain' : 1,
        'Ajax_RequestUrl' : 'http://movie.mtime.com/movie/search/section/#',
        't' : '201693014374394791',
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
    sleep_time = 2
    year = 0
    while True:
        if empty_time > 5 :
            break
        try:
            year = year_queue.get(0)
        except:
            sleep(sleep_time)
            empty_time += 1
            continue

        print thread_id, "parsing year", year
        logging.info(str(thread_id) +  " parsing year " + str(year))
        
        i = 1                   # 页码
        page_stop_flag = 0
        while i < 10001:
            # 如果停止翻页标志位=1， 跳出翻页循环
            if page_stop_flag == 1:
                break
            data['Ajax_CallBackArgument18'] = i;    # 设置页码
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
                logging.warning('载入 '+ str(year) + '年' + str(i) + '页网页内容出错, 停止爬取')
                break

            # 改用正则表达式匹配
            html = ''
            if response_json.has_key('value') and response_json['value'].has_key('listHTML'):
                html = response_json['value']['listHTML']
            else:
                if response_json.has_key('value'):
                    logging.warning('载入 '+ str(year) + '年' + str(i) + '页网页内容出错, 停止爬取')
                    break

            lst = re.findall(u'<h3 class=\"normal mt6\"><a.*?href=\"(.*?)\">(.*?)</a>', html)
            if len(lst) == 0:
                logging.warning('匹配 '+ str(year) + '年' + str(i) + '页电影信息出错, 忽略该页')
                i += 1
                continue

            movie_url_list, movie_name_list = zip(*lst)
            comment_counts_list = re.findall(u'<p class=\"c_666 mt6\">(\d*?人评分)</p>', html)
            if not len(movie_url_list) == len(movie_name_list) == len(comment_counts_list):
                logging.warning(str(year) + '年' + str(i) + '页电影信息数量不匹配, 忽略该页')
                i += 1
                continue
                
            if len(movie_url_list) == len(movie_name_list) == len(comment_counts_list):
                for index, text in enumerate(comment_counts_list):
                    if page_stop_flag == 1:
                        logging.info(str(thread_id) + " 评分人数少于 "+str(least_comment_num)+", 不再翻页")
                        break
                    comment_num = int(text.replace(u'人评分', ''))
                    if comment_num >= least_comment_num:
                        movie_name = movie_name_list[index].encode('utf8')
                        detail_url = movie_url_list[index].encode('utf8')
                        detail_r = requests.get(detail_url)

                        # 剧情信息
                        plots_url = detail_url + 'plots.html'
                        plots_html = requests.get(plots_url, headers=headers).content
                        plots_text = ''
                        soup = BeautifulSoup(plots_html, 'lxml') # making soup
                        try:
                            plots_text = [tag.text for tag in soup.select('div[class="plots_box"] p')][0]
                        except:
                            pass
                        plots_text = plots_text.strip()
                        
                        # 导演信息
                        director_lst = re.findall('<a.*?rel="v:directedBy">(.*?)</a>', detail_r.content)
                        if len(director_lst) > 0:
                            director = text_filter(director_lst[0])

                        # 领衔主演信息
                        starring_lst = re.findall('<a.*?rel="v:starring">(.*?)</a>', detail_r.content)
                        if len(starring_lst) > 0:
                            starring = text_filter(starring_lst[0])
                        
                        # 主演信息（包括领衔主演）
                        actor_url = detail_url + 'fullcredits.html'
                        actor_list = []
                        html = requests.get(actor_url, headers=headers).content
                        actor_character_patt = \
                        '<dd>.*?class=\"actor_tit\".*?<h3>.*?<a.*?>(.*?)</a>.*?class=\"character_tit\">.*?<h3>(.*?)</h3>.*?</dd>'
                        actor_character_list = re.findall(actor_character_patt, html)
                        print u"演员表和人物表", len(actor_character_list)
                        actor_list.extend([(text_filter(x), text_filter(y)) for x, y in actor_character_list[:20]])

                        # 影片评论
                        comment_list = []
                        for k in range(1, 11):
                            comment_url = detail_url + 'reviews/short/new'
                            if k==1:
                                comment_url += '.html'
                            else:
                                comment_url += '-' + str(k) + '.html'
                            print comment_url
                            comment_r = requests.get(comment_url, headers=headers)
                            comment_html = comment_r.content
                            comment_patt = \
                            '<div tweetid=\"\d{1,10}\".*?class=\"mod_short\">.*?<h3>(.*?)</h3>.*?<span class=\"db_point ml6\">(.*?)</span>'
                            comment_patt_no_score = \
                            '<div tweetid=\"\d{1,10}\".*?class=\"mod_short\">.*?<h3>(.*?)</h3>.*?<p class=\"mt6 px12 clearfix\">(.*?)</p>'
                            tmp_list = re.findall(comment_patt_no_score, comment_html)
                            
                            for item in tmp_list:
                                comment_text = item[0]
                                lst = re.findall('<span class=\"db_point ml6\">(.*?)</span>', item[1])
                                if len(lst) == 1:
                                    comment_score = float(lst[0])
                                else:
                                    # print u"此用户没有评分"
                                    comment_score = -1.0
                                comment_list.append((comment_text, comment_score))
                            
                            sleep(1 + random.uniform(0, 2))

                        print thread_id, movie_name_list[index], comment_num, director.decode('utf8'), year

                        record_item = {
                            'movie_name': movie_name,
                            'show_year': year,
                            'comment_counts': comment_num,
                            'plots_text': plots_text,
                            'director': director,
                            'starring': starring,
                            'url': detail_url,
                            'comment_list': comment_list,
                            'actor_list': actor_list,
                        }
                        mtime_db.insert_one_record(record_item)
                    else:
                        print thread_id, u"评分人数少于", least_comment_num, u"不再翻页"
                        page_stop_flag = 1
                    sleep(1 + random.uniform(0, 5))             # 爬完一部电影的全部信息，需要休息一段时间
            i += 1
            sleep(6 + random.uniform(0, 5))             # 爬完一页20部电影信息，需要休息足够久


def main(start_year, end_year, thread_num, least_comment_num):
    q = Queue(50)
    year_lst = range(start_year, end_year+1)
    for item in year_lst:
        q.put(item, 1)
    threads = []

    for i in range(thread_num):
        t = spider_thread(mtime_spider, ('mtime_crawler'+str(i+1), q, least_comment_num), 'crawler'+str(i+1))
        threads.append(t)

    for i in range(thread_num):
        threads[i].start()

    for i in range(thread_num):
        threads[i].join()


if __name__ == '__main__':
    
    start = datetime.now()

    start_year = 2016
    end_year = 2016
    mtime_db.collection = mtime_db.db['mtime_movie_'+str(start_year)+'_'+str(end_year)]
    thread_num = 2
    least_comment_num = 100
    main(start_year, end_year, thread_num, least_comment_num)

    end = datetime.now()

    print u"耗时：", end - start
