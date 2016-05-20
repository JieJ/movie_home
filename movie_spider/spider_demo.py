# -*- coding: utf-8 -*-
"""
定义一个爬虫，其静态方法为爬取主函数，同时充当生产者和消费者
"""
import requests
import os
import re
import time

from Queue import Queue
from time import sleep
from datetime import datetime

from bs4 import BeautifulSoup
from lxml import etree

from spider import spider
from spider_thread import spider_thread
from spider_db import ys66_db

class ys66_spider(spider):
    def __init__(self):
        pass

    @classmethod
    def crawler(self, thread_id, url_queue, logger_handle, deadline):
        page_stop_flag = 0
        empty_time = 0
        sleep_time = 5
        url = ''
        while True:
            if empty_time > 100 :
                break
            try:
                url = url_queue.get(0)
                print "\n consumed url from Q size now", url_queue.qsize()
                # print "size now", url_queue.qsize()
            except:
                sleep(sleep_time)
                empty_time += 1
                continue

            if re.search('http://www.66ys.tv/\w*?/index\_?\d{0,4}\.html', url) is not None:


                try:
                    response = requests.get(url)
                except:
                    logger_handle.write(url + ' page request wrong')

                # dom = etree.HTML(response.content)
                soup = BeautifulSoup(response.content, 'lxml') # making soup

                logger_handle.write(url + 'parsing page for upload_time & url_link ...' + '\n')

                upload_time_list = [tag.find_all('p')[2].text for tag in soup.select('div[class="listInfo"]')]
                # upload_time_list = dom.xpath(self.upload_time_xpath)

                url_list = [tag['href'] for tag in soup.select('div[class="listInfo"] h3 a')]
                # url_list = dom.xpath(self.url_xpath)

                print len(url_list), len(upload_time_list)
                if len(url_list) == len(upload_time_list):
                    for time_str, url_str in zip(upload_time_list, url_list):

                        # 如果上传时间在设定时间之前，则停止解析当前列表页，并且设置不再翻页
                        time_stamp = time.mktime(time.strptime(time_str.lstrip(u'时间：'), '%Y-%m-%d'))
                        if time_stamp < deadline:
                            page_stop_flag = 1
                            break
                        print "producing url for Q..."
                        # logger_handle.write('producing new movie detail info url ...' + '\n')
                        url_queue.put(url_str, 1)

                if page_stop_flag == 0:
                    # get next page url
                    next_page_tag = soup.find_all('a', text = u'下一页')
                    if len(next_page_tag) > 0:
                        next_page_url = next_page_tag[0]['href']
                        # print "producing url for Q..."
                        # logger_handle.write('producing new movie list page url ...' + '\n')
                        url_queue.put(next_page_url, 1)
                        # print "size now", url_queue.qsize()
            else:
                logger_handle.write('thread ' + thread_id + 'parsing detail page' + url + '\n')
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'lxml') # making soup

                # get movie type from url
                movie_type = ''
                try:
                    movie_type = re.findall('http://www.66ys.tv/(.*?)/.*', url)[0]
                    movie_type = movie_type.encode('utf8')
                except IndexError:
                    logger_handle.write(url + ' movie_type index out of range '+'\n')
                    print "index out of range"

                # get movie name by xpath
                movie_name = ''
                movie_name_tag = soup.select('div[class="contentinfo"] h1')
                try:
                    movie_name = movie_name_tag[0].text.strip().strip(u'《').strip(u'》').encode('utf8')
                except IndexError:
                    logger_handle.write(url + ' movie_name index out of range '+'\n')
                    print "index out of range"

                # get ftp or http download info
                download_info = []
                download_link_list = [x['href'] for x in soup.select('div#text table tbody tr td a[href]')]
                download_filename_list = [x.text for x in soup.select('div#text table tbody tr td a')]
                if len(download_filename_list)==len(download_link_list):
                    for x,y in zip(download_filename_list, download_link_list):
                        if u'pan.baidu.com' in x:
                            continue
                        if u'在线观看' in x:
                            continue
                        if y.startswith(u'http'):
                            continue
                        tmp_info = {}
                        tmp_info['download_filename'] = x.encode('utf8')
                        tmp_info['download_link'] = y.encode('utf8')
                        download_info.append(tmp_info)

                # # get wangpan link info
                try:
                    utf8_body = unicode(response.content, 'gbk').encode('utf8','ignore')
                except UnicodeDecodeError:
                    # print u"编码转换错误"
                    logger_handle.write('Encode/Decode Error in ' + url + '\n')
                    continue
                wangpan_info = []
                wangpan_patt = '网盘[\w\W]*?>(.*?)</a> 密码：(.*?)</td>'
                wangpan_lst = re.findall(wangpan_patt, utf8_body)
                for pan in wangpan_lst:
                    tmp_pan_info = {}
                    tmp_pan_info['wangpan_link'] = pan[0]
                    tmp_pan_info['wangpan_pwd'] = pan[1]
                    wangpan_info.append(tmp_pan_info)

                if len(download_info) > 0 or len(wangpan_info) > 0:
                    record_item = {
                        'movie_name' : movie_name,
                        'movie_type' : movie_type,
                        'movie_url' : url,
                        'download_info' : download_info,
                        'wangpan_info' : wangpan_info,
                    }
                    ys66_db.insert_one_record(record_item)
                else:
                    logger_handle.write('no download_info in' + url + '\n')



def main(start_url, thread_num, last_crawled_date):

    deadline = time.mktime(time.strptime(last_crawled_date, '%Y-%m-%d'))
    q = Queue(50)
    for item in start_url:
        q.put(item, 1)
    # q.put('http://www.66ys.tv/xijupian/index.html', 1)
    # q.put('http://www.66ys.tv/aiqingpian/index.html', 1)
    threads = []
    logger_handle = open('logger2.txt', 'a')
    for i in range(thread_num):
        t = spider_thread(ys66_spider.crawler, ('crawler'+str(i+1), q, logger_handle, deadline), 'crawler'+str(i+1))
        threads.append(t)

    for i in range(thread_num):
        threads[i].start()

    for i in range(thread_num):
        threads[i].join()

    logger_handle.close()

if __name__ == '__main__':

    start = datetime.now()
    start_url = [
        # 'http://www.66ys.tv/xijupian/index.html',
        # 'http://www.66ys.tv/aiqingpian/index.html',
        'http://www.66ys.tv/dongzuopian/index.html',
        # 'http://www.66ys.tv/kehuanpian/index.html',
        # 'http://www.66ys.tv/zhanzhengpian/index.html',
        # 'http://www.66ys.tv/kongbupian/index.html',
        # 'http://www.66ys.tv/jilupian/index.html',
        # 'http://www.66ys.tv/bd/index.html',
        # 'http://www.66ys.tv/3ddy/index.html',
    ]
    last_crawled_date = '2000-05-01'
    thread_num = 5
    main(start_url, thread_num, last_crawled_date)
    end = datetime.now()

    print u"耗时：", end - start

