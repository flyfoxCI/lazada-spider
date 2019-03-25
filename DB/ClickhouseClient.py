#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------------------------------
 File    : ClickhouseClient.py
 Time    : 2017/12/15 16:33
 Author  : jerry
 Description  : 
------------------------------------------
 Change Activity:
------------------------------------------
"""
import sqlalchemy as sa
import time
from Util.GetConfig import GetConfig


class ClickHouseClient(object):
    def __init__(self):
        self.config = GetConfig()
        self.client = sa.create_engine(self.config.click_url)

    def insert(self, url, level):
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        insertStr = r"insert into lazada_crawl_url values('"+str(url)+"',"+str(level)+",'new','"+now+"','"+now+"');"
        print insertStr
        return self.client.execute(insertStr)


    def get(self):
        query = "select url from lazada_crawl_url where status='new' LIMIT 1"
        record = self.client.execute(query)
        if record:
            print record.cursor._data[0][0]
            updateStr = "update lazada_crawl_url set status='downloading'"  + " ,updateTime='" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "' where url='" + record.cursor._data[0][0]+"'"
            print updateStr
            self.client.execute(updateStr)
        return record

    def update(self, status, url):
        query = "select * from lazada_crawl_url where url=" + url
        result = self.client.execute(query)
        if result:
            updateStr = "update lazada_crawl_url set status=" + status + " ,updateTime=" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " where url=" + url
            self.client.execute(updateStr)


if __name__ == '__main__':
    client = ClickHouseClient()
    client.insert("wwww.mafengwo.cn/xxxx",1)
    client.get()
