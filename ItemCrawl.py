#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------------------------------
 File    : Crawl.py
 Time    : 2017/12/15 12:46
 Author  : jerry
 Description  : 
------------------------------------------
 Change Activity:
------------------------------------------
"""
import threading
import gevent
import gevent.pool, gevent.thread, gevent.monkey
from multiprocessing import Pool

from DB.MongoSsdbUrlManager import MongoSsdbUrlManager
from Process.SubMenuUrlHandler import SubMenuUrlHandler
import traceback
manager = MongoSsdbUrlManager()
def getContent():
    # get url from mongoDB judge handler from different depth
    # get content
    # enqueue new url
    try:
        url = manager.dequeue_url(1)
        submenu = SubMenuUrlHandler()
        while url is not None:
            submenu.handle(url['url'])
            url = manager.dequeue_url(1)
    except Exception as  e:
         print("exception: {0}".format(e))
         traceback.print_exc()

    # finally:
    #     submenu.driver.quit()


def start(thread_num):
    pool = Pool(processes=thread_num)
    for i in xrange(thread_num):
        pool.apply_async(getContent, args=())
    pool.close()
    pool.join()
    return pool

if __name__ == '__main__':
    pool = start(20)


