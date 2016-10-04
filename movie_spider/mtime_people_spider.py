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
from bs4 import BeautifulSoup

from Queue import Queue
from time import sleep

from spider import spider
from spider_thread import spider_thread
from spider_db import mtime_db_actor
from spider_db import mtime_db_director

import sys

# log_file = open("message.log", "w")
# # redirect print output to log file
# sys.stdout = log_file

import logging  
logging.basicConfig(level=logging.DEBUG,  
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  
                    datefmt='%a, %d %b %Y %H:%M:%S',  
                    filename='test.log',  
                    filemode='a')

def text_filter(ss):
    return ss.replace('·', '-').replace('&#183;', '-')

def mtime_people_spider(thread_id, page_queue, least_comment_num, people_type):
    url = 'http://service.channel.mtime.com/service/search.mcs'
    data = {
        'Ajax_CallBack' : 'true',
        'Ajax_CallBackType' : 'Mtime.Channel.Pages.SearchService',
        'Ajax_CallBackMethod' : 'SearchPersonByCategory',
        'Ajax_CrossDomain' : 1,            
        'Ajax_RequestUrl' : 'http://movie.mtime.com/people/search/section/#',
        't' : '20161021626424256',
        'Ajax_CallBackArgument1':0,
        'Ajax_CallBackArgument2':0,
        'Ajax_CallBackArgument3':100,
        'Ajax_CallBackArgument4':people_type,     # 类型标识 1：演员 2：导演
        'Ajax_CallBackArgument5':0,
        'Ajax_CallBackArgument6':0,
        'Ajax_CallBackArgument7':0,
        'Ajax_CallBackArgument8':0,
        'Ajax_CallBackArgument9':0,
        'Ajax_CallBackArgument10':0,
        'Ajax_CallBackArgument11':4,    # 排序指标  4：按照评分人数排序
        # 'Ajax_CallBackArgument12':1,  # page_index
        'Ajax_CallBackArgument13':0,
    }

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

    sleep_time = 2
    while page_queue.qsize() > 0:
        try:
            page = page_queue.get(0)
            # print "\n consumed url from Q size now", page_queue.qsize()
            # print "size now", page_queue.qsize()
        except:
            sleep(sleep_time)
            continue
        
        print thread_id, "parsing page", page
        logging.info(str(thread_id) +  " parsing page " + str(page))
        data['Ajax_CallBackArgument12'] = page;    # 设置页码

        r = requests.get(url, headers=headers, params=data) 
        content = re.findall('.*?(\{.*\}).*', r.content)[0]

        response_json = {}
        try:
            response_json = json.loads(content)
        except:
            logging.info(str(thread_id) +  " page " + str(page) + " 未发现返回信息\n")
            print thread_id, "page=", page, u"未发现返回信息"
            break

        html = ''
        if response_json.has_key('value') and response_json['value'].has_key('html'):
            html = response_json['value']['html']
        else:
            logging.info(str(thread_id) +  " page " + str(page) + " 未发现返回信息\n")
            print thread_id, "page=", page, u"未发现返回信息"
            break
        
        html = html.replace(u'\"', '"').encode('utf8')
        soup = BeautifulSoup(html, 'lxml')          # making soup

        # 链接，评分人数, 评分
        url_lst = [tag.a['href'] for tag in soup.find_all("h3", class_ = "normal mt6")]
        comment_counts_lst = [tag.text for tag in soup.find_all("p", class_ = "c_666 mt6")]
        comment_score_lst = [tag1.text+tag2.text for tag1, tag2 in zip(soup.find_all('span', class_='total'), \
        soup.find_all('span', class_ = 'total2'))]

        # print len(url_lst), len(comment_counts_lst), len(comment_score_lst)
        
        if len(url_lst) != len(comment_counts_lst) or len(url_lst) != len(comment_score_lst):
            logging.warning(str(thread_id) +  " page " + str(page) + " 信息数量不匹配\n")
            print u"信息数量不匹配"
            continue
        
        print "page=", page, len(url_lst), len(comment_counts_lst), len(comment_score_lst)
        
        for index, text in enumerate(comment_counts_lst):
            comment_counts = int(text.replace(u'人评分', ''))
            if comment_counts < least_comment_num:
                print thread_id, u"评分人数少于", least_comment_num, u"此页不再爬取"
                continue
            
            people_url = url_lst[index].encode('utf8')
            people_html = requests.get(people_url).content

            # 数据库编号，中文名，英文名，职业，得分，出生日期
            soup = BeautifulSoup(people_html, 'lxml') # making soup
            zh_name = [tag.text for tag in soup.select('div[class="per_header"] h2')][0] 
            
            tmp_lst = [tag.text for tag in soup.select('div[class="per_header"] p')]
            try:
                en_name, profession = tmp_lst[0], tmp_lst[1]
                profession = re.sub('\r\n', '', profession).strip()
            except:
                logging.warning(people_url + " 英文姓名，职业信息匹配有误\n")
                print people_url, u"英文姓名，职业信息匹配有误"
            
            comment_score =  float(comment_score_lst[index])
            
            detail_url = people_url + 'details.html'
            detail_html = requests.get(detail_url, headers=headers).content
            soup = BeautifulSoup(detail_html, 'lxml') # making soup
            tmp_lst = [tag.text for tag in soup.select('dl[class=per_info_cont] dt')]
            # birthday, height, weight = tmp_lst[0], tmp_lst[1], tmp_lst[2]
            birthday = ''
            if len(tmp_lst) > 0:
                birthday += tmp_lst[0]
            birthday = birthday.replace(u'出生日期：', u'').strip()
            
            # try:
            #     print zh_name.encode('gbk', 'ignore'), en_name.encode('gbk', 'ignore'), \
            #     profession.encode('gbk', 'ignore'), birthday.encode('gbk', 'ignore'), comment_score
            # except:
            #     pass

            character_id = people_url.strip('/').replace('http://people.mtime.com/', '')
            update_filter = {
                'character_id':character_id,
            }
            record_item = {
                'character_id':character_id,
                'url': people_url,
                'zh_name': zh_name,
                'en_name': en_name,
                'comment_counts': comment_counts,
                'comment_score': comment_score,
                'profession': profession,
                'birthday': birthday,
            }
            if people_type == 1:
                # mtime_db_actor.insert_one_record(record_item)
                mtime_db_actor.update_one_record(update_filter, {"$set":record_item})
            if people_type == 2:
                # mtime_db_director.insert_one_record(record_item)
                mtime_db_director.update_one_record(update_filter,  {"$set":record_item})

        sleep(6 + random.uniform(0, 3))


def main(page_lst, thread_num, least_comment_num, people_type):
    q = Queue(200)
    for item in page_lst:
        q.put(item, 1)
    threads = []
    for i in range(thread_num):
        t = spider_thread(mtime_people_spider, ('mtime_crawler'+str(i+1), q, least_comment_num, people_type), 'crawler'+str(i+1))
        threads.append(t)

    for i in range(thread_num):
        threads[i].start()

    for i in range(thread_num):
        threads[i].join()


if __name__ == '__main__':

    start = datetime.now()
    page_lst = range(1, 141)
    page_lst = range(11, 81)
    thread_num = 2
    least_comment_num = 1
    people_type = 2

    main(page_lst, thread_num, least_comment_num, people_type)
    
    end = datetime.now()
    print u"耗时：", end - start
    # log_file.close()