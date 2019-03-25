#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------------------------------
 File    : SubMenuUrlHandler.py
 Time    : 2017/12/16 15:28
 Author  : jerry
 Description  : catch the item below submenus
------------------------------------------
 Change Activity:
------------------------------------------
"""
import UrlHandler
from lxml import etree
from GetWebDriver import GetWebDriver
from DB.MongoSsdbUrlManager import MongoSsdbUrlManager
import traceback
import time

class SubMenuUrlHandler():
    def __init__(self):
        self.manager = MongoSsdbUrlManager()
        self.driver = GetWebDriver.getDriver()

    def put_table_items(self, page_url):
        if str(page_url).endswith("/"):
            page_url += "?itemperpage=120&sc=EbQZ"
        else:
            page_url += "&itemperpage=120&sc=EbQZ"
        for i in xrange(1, 30):
            url = str(page_url) + "&page=" + str(i)
            try:
                self.driver.get(url)
                time.sleep(5)
                if self.driver.page_source is None:
                    break
                self.driver.execute_script("window.scrollBy(0,15000)")
                content = etree.HTML(self.driver.page_source)
                table_items = content.xpath("//div[@class='c16H9d']/a/@href")
                for item in table_items:
                    comlete_url = "https://www.lazada.co.id" + str(item)
                    self.manager.enqueue_url(comlete_url, 'new', 3)
            except Exception as e:
                print e.message, e.args
                print traceback.print_exc()
                self.manager.save_error(url, 'new', 2)
                self.driver.close()
                time.sleep(60)

                # self.driver = GetWebDriver.set_proxy(self.driver)



    def handle(self, url):
        try:
            self.driver.get(url)
            '''滑动滚动条到底部'''
            self.driver.execute_script("window.scrollBy(0,15000)")
            content = etree.HTML(self.driver.page_source)
            carousel_items = content.xpath(
                "//div[contains(@class,'c-slider__slide') and "
                "contains(@class,'c-slider__slide_10-2') and "
                "contains(@class,'c-slider__slide_sm-8-2')]/a/@href")
            self.put_table_items(url)
            for item in carousel_items:
                self.manager.enqueue_url(item, 'new', 3)
            self.manager.finish_url(url)
        except Exception as e:
            print e.message,e.args
            print traceback.print_exc()
            self.manager.save_error(url, 'new', 1)
            self.driver.close()
            time.sleep(10)
            # self.driver = GetWebDriver.set_proxy(self.driver)


        # page_url = content.xpath(
        #     "//a[contains(@class,'c-paging__link') and contains(@class,'c-paging__link-current')]/@href")
        # if len(page_url) > 0:

