#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------------------------------
 File    : MongoSsdbUrlManager.py
 Time    : 2017/12/16 12:54
 Author  : jerry
 Description  : 
------------------------------------------
 Change Activity:
------------------------------------------
"""
import hashlib

import pymongo
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING

from DB.DbClient import DbClient
from Util.GetConfig import GetConfig


class MongoSsdbUrlManager(object):
    def __init__(self, host="localhost", client=None):
        self.config = GetConfig()
        self.client = MongoClient('mongodb://localhost:27017/') if client is None else client
        self.ssdb_client = DbClient()
        self.db = self.client.spider
        if self.db.lazada.count() is 0:
            self.db.lazada.create_index([("status", ASCENDING),
                                         ("pr", DESCENDING)])

    def enqueue_url(self, url, status, depth):
        md5 = hashlib.md5(url).hexdigest()
        i = 0
        while i < 2:
            try:
                num = self.ssdb_client.get(md5)
                if num is not None:
                    self.ssdb_client.update(key=md5, value=int(num) + 1)
                    return
                self.ssdb_client.put(md5)
                i = 2
            except Exception as error:
                print error
                i += 1
        self.db.lazada.save({
            '_id': md5,
            'url': url,
            'status': status,
            'queue_time': datetime.utcnow(),
            'depth': depth,
            'pr': 0
        })

    def dequeue_url(self, depth):
        # record = self.db.lazada.find_one_and_update(
        #     {'status': 'downloading', 'depth': depth},
        #     {'$set': {'status': 'downloading'}},
        #     upsert=False,
        #     sort=[('pr', DESCENDING)],  # sort by pr in descending
        #     returnNewDocument=False
        # )

        record = self.db.lazada.find_one(
            {'status': 'downloading', 'depth': depth}
        )

        if record:
            return record
        else:
            return None

    def finish_url(self, url):
        record = {'status': 'done', 'done_time': datetime.utcnow()}
        self.db.lazada.update({'_id': hashlib.md5(url).hexdigest()}, {'$set': record}, upsert=False)

    def clear(self):
        self.ssdb_client.clear()

    def save_error(self, url, status, depth):
        md5 = hashlib.md5(url).hexdigest()
        self.db.lazada_error.save({
            '_id': md5,
            'url': url,
            'status': status,
            'queue_time': datetime.utcnow(),
            'depth': depth,
            'pr': 0
        })

    def update(self):
        self.db.lazada.update({'status': 'downloading'}, {'$set': {'status': 'new'}}, multi=True)


    def save(self, record):
        self.db.record.save(record)

if __name__ == '__main__':
    manager = MongoSsdbUrlManager()
    manager.update()
    manager.clear()