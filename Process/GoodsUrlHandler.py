#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------------------------------
 File    : GoodsUrlHandler.py
 Time    : 2017/12/17 10:56
 Author  : jerry
 Description  : 
------------------------------------------
 Change Activity:
------------------------------------------
"""
from GetWebDriver import GetWebDriver
from DB.MongoSsdbUrlManager import MongoSsdbUrlManager
from lxml import etree
import re
import urllib2
import json
import time


class GoodUrlHandler(object):

    def __init__(self, prefix):
        self.manager = MongoSsdbUrlManager()
        self.driver = GetWebDriver.getDriver()
        self.prefix = prefix

    def get_category(self, content):
        categories = content.xpath("//ul/li/span[@class='breadcrumb__item-text']/a/span/text()")
        name = str(content.xpath("//ul/li[@class='breadcrumb__item breadcrumb__item_pos_last']/span/text()")[0])
        return name, categories

    def get_good_price(self, content):
        spans = content.xpath("//div[@class='prod_pricebox_price_final']/span/text()")
        unit = spans[1]
        discount_price = str(unit) + " "+spans[2]
        origin_price = str(content.xpath("//div[@id='special_price_area']/span[@class='price_erase']/span["
                                     "@id='price_box']/text()")[0])
        if origin_price.endswith(","):
            origin_price = origin_price.replace(",", "")
        return origin_price, discount_price

    def get_good_features(self, content):
        good_features = dict()
        kvs = content.xpath("//div[@class='product-description__block']/table/tbody/tr/td/text()")
        i = 0
        while i < len(kvs):
            good_features[kvs[i]] = kvs[i + 1]
            i += 2
        return good_features

    def get_seller_detail(self, content):
        seller_detail = dict()
        name = content.xpath("//div[@class='basic-info__main']/a/text()")[0]
        seller_href = content.xpath("//div[@class='basic-info__main']/a/@href")
        rate = content.xpath(
            "//div[contains(@class,'c-positive-seller-ratings') and contains(@class,'c-positive-seller-ratings_state_medium')]/text()")[
            0].replace("\n", "").strip()
        seller_detail['name'] = name
        seller_detail['href'] = seller_href[0]
        seller_detail['rate'] = rate[0]
        return seller_detail

    def get_questions(self, content):
        qa_div = content.xpath("//div[@class='c-product-qa__heads-wrap']/div/span/text()")
        if qa_div is not None:
            count = qa_div[0][1:-1]
            return count
        else:
            return 0

    def get_comments(self, content, sku):
        global comment_data
        score = str(content.xpath("//div[@class='c-rating-total__text-rating-average']/em/text()")[0])
        stars_num_count = content.xpath(
            "//ul[@class='c-rating-bar-list']/li/span[@class='c-rating-bar-list__count']/text()")
        stars_num_count = [str(i).replace("\n", "").strip() for i in stars_num_count]
        num_str = content.xpath("//div[@class='c-rating-total__text-total-review']/text()")[0]
        v = re.findall(r"\d{1,}", str(num_str))
        total_score_num = int(v[0])
        comment_num = int(v[1])
        comment_data = []
        if comment_num is not None:
            page_num = comment_num // 10 + 1
            for i in xrange(1, page_num):
                url = self.prefix + "/ajax/ratingreview/reviewspage?page=" + str(
                    i) + "&sort=relevance&sortDirection=desc&sku=" + str(sku)
                req = urllib2.Request(url)
                response = urllib2.urlopen(req)
                time.sleep(3)
                comment_content = response.read()
                data = json.loads(comment_content)
                comment_data.append(data['data']['ratingReviews'])
        return score, stars_num_count, total_score_num, comment_num, comment_data

    def get_good_detail(self, content):
        description_title = content.xpath("//div[@class='product-description__block']/h2/text()")
        description_text = content.xpath("//div[@class='product-description__block']/ul/li/text()")
        description_img_href = content.xpath("//img[@class='productlazyimage']/@data-original")
        return description_title, description_text, description_img_href

    def handle(self, url):
        record = dict()
        self.driver.get(url)
        self.driver.execute_script("window.scrollBy(0,3700)")
        content = etree.HTML(self.driver.page_source)
        name, categories = self.get_category(content)
        record['name'] = name
        record['categories'] = json.dumps(categories)
        good_featurte = self.get_good_features(content)
        record['good_featurte'] = good_featurte
        seller_detail = self.get_seller_detail(content)
        record['seller_detail'] = seller_detail
        question_count = self.get_questions(content)
        record['question_count'] = question_count
        score, stars_num_count, total_score_num, comment_num, comment_data = self.get_comments(content, good_featurte['SKU'].split("-")[0])
        record['score'] = score
        record['stars_num'] = json.dumps(stars_num_count)
        record['total_score_num'] = total_score_num
        record['comment_num'] = comment_num
        record['comment_data'] = json.dumps(comment_data)

        description_title, description_text, description_img_href = self.get_good_detail(content)
        record['description_title'] = json.dumps(description_title)
        record['description_text'] = json.dumps(description_text)
        record['description_img_href'] = json.dumps(description_img_href)
        origin_price, discount_price = self.get_good_price(content)
        record['origin_price'] = origin_price
        record['discount_price'] = discount_price
        self.save(record)

    def save(self, record):
        self.manager.save(record)

if __name__ == '__main__':

    handler = GoodUrlHandler("https://www.lazada.com.my")
    try:
        print time.time()
        c = handler.handle(
            "https://www.lazada.com.my/amart-fashion-women-flat-shoes-spring-rose-embroidery-platform-casual-shoesblack-63716561.html?spm=a2o4k.prod.0.0.7d285affGeUerp")
        print time.time()
    except Exception as e:
        print e
    finally:
        handler.driver.quit()
