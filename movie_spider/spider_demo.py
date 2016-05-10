# -*- coding: utf-8 -*-
"""
定义一个爬虫，其静态方法为爬取主函数，同时充当生产者和消费者
"""
import requests
import os
import re
from Queue import Queue
from lxml import etree
from time import sleep
from spider import spider
from spider_thread import spider_thread


class ys66_spider(spider):
    movie_name_xpath = '//div[@class="listBox"]/ul/li/div[@class="listInfo"]/h3/a/text()'
    url_xpath = '//div[@class="listBox"]/ul/li/div[@class="listInfo"]/h3/a/@href'
    upload_time_xpath = '//div[@class="listBox"]/ul/li/div[@class="listInfo"]/p[3]/text()'

    def __init__(self, spider_name):
        spider.__init__(self)
        self.spider_name = spider_name

    @classmethod
    def crawler(self, url_queue, file_handle):
        empty_time = 0
        url = ''
        movie_name_xpath, url_xpath, upload_time_xpath = self.movie_name_xpath, \
        self.url_xpath, self.upload_time_xpath
        while True:
            if empty_time > 10 :
                break
            try:
                url = url_queue.get(0)
                print "\n consumed url from Q size now", url_queue.qsize()
                print "size now", url_queue.qsize()
            except:
                sleep(4)
                empty_time += 1

            if re.search('http://www.66ys.tv/xijupian/index\_?\d{0,4}\.html', url) is not None:

                response = requests.get(url)
                dom = etree.HTML(response.content)

                movie_name_list = dom.xpath(movie_name_xpath)
                upload_time_list = dom.xpath(upload_time_xpath)
                url_list = dom.xpath(url_xpath)
                sleep(3)
                print len(movie_name_list), len(url_list), len(upload_time_list)
                if len(movie_name_list) == len(url_list) == len(upload_time_list):
                    for a, b, c in zip(movie_name_list, upload_time_list, url_list):
                        print "producing url for Q..."
                        url_queue.put(c, 1)
                        print "size now", url_queue.qsize()
                        lst = map(lambda x: x.encode('utf8', 'ignore'), [a, b, c])
                        try:
                            file_handle.write('\t'.join(lst) + '\n')
                        except:
                            print "IO ERROR"
                        sleep(0.5)
                lst = re.findall('http://www.66ys.tv/xijupian/index_?(\d{1,4})\.html', url)
                if len(lst) == 0:
                    print "producing url for Q..."
                    url_queue.put(u'http://www.66ys.tv/xijupian/index_2.html', 1)
                    print "size now", url_queue.qsize()
                    sleep(0.5)
                elif int(lst[0]) < 2:
                    print "producing url for Q..."
                    url_queue.put(u'http://www.66ys.tv/xijupian/index_' + str(int(lst[0])+1) + u'2.html', 1)
                    print "size now", url_queue.qsize()
                    sleep(0.5)
                else:
                    pass
            else:
                # parser_2(url)
                pass

def main():
    q = Queue(32)
    q.put('http://www.66ys.tv/xijupian/index.html', 1)

    threads = []
    num = 5
    f = open('movie.txt', 'w')
    for i in range(num):
        t = spider_thread(ys66_spider.crawler, (q, f), 't'+str(i+1))
        threads.append(t)

    for i in range(num):
        threads[i].start()

    for i in range(num):
        threads[i].join()
    f.close()

if __name__ == '__main__':
    main()
