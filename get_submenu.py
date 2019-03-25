import hashlib

from lxml import etree
from selenium import webdriver
from DB.DbClient import DbClient
from DB.MongoSsdbUrlManager import  MongoSsdbUrlManager
from GetWebDriver import GetWebDriver

root_url = "https://www.lazada.co.id"
driver = GetWebDriver.getDriver()
driver.get(root_url)
content = driver.page_source
html = etree.HTML(content)
submenus = html.xpath("//nav/span")
manager = MongoSsdbUrlManager()
for ix, submenu in enumerate(submenus):
    index = ix+1
    driver.find_element_by_xpath("//nav/span["+str(index)+"]").click()
    hrefs = etree.HTML(driver.page_source).xpath("//a[@class='js-second-menu__item']/@href")
    for href in hrefs:
        manager.enqueue_url(href,'new',1)






