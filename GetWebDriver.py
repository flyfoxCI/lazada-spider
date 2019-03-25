#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
------------------------------------------
 File    : GetWebDriver.py
 Time    : 2017/12/16 15:39
 Author  : jerry
 Description  : 
------------------------------------------
 Change Activity:
------------------------------------------
"""
from telnetlib import EC

from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.proxy import ProxyType, Proxy
from selenium.webdriver.support.wait import WebDriverWait
import urllib


class GetWebDriver():
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Charset': 'utf-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
        'Connection': 'keep-alive'
    }


    @staticmethod
    def getDriver(locator=None):
        service_args = []
        service_args.append('--load-images=no')  ##关闭图片加载
        service_args.append('--disk-cache=yes')  ##开启缓存
        service_args.append('--ignore-ssl-errors=true')  ##忽略https错误
        for key, value in GetWebDriver.headers.iteritems():
            webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value

        # another way to set custome header
        webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = \
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'

        driver = webdriver.PhantomJS(r"F:\develop\phantomjs-2.1.1-windows\bin\phantomjs.exe", service_args=service_args)
        driver.set_window_size(1024, 2400)
        driver.implicitly_wait(60)  ##设置超时时间
        driver.set_page_load_timeout(60)  ##设置超时时间
        return driver

    @staticmethod
    def set_proxy(driver):
        url = "http://127.0.0.1:5010/get/"
        try:
            resp = urllib.urlopen(url).read()
            ip_port = str(resp)
            proxy = Proxy(
                {
                    'proxyType': ProxyType.MANUAL,
                    'httpProxy': 'ip:port'  # 代理ip和端口
                }
            )
            # 再新建一个“期望技能”，（）
            desired_capabilities = DesiredCapabilities.PHANTOMJS.copy()
            # 把代理ip加入到技能中
            proxy.add_to_capabilities(desired_capabilities)
            # 新建一个会话，并把技能传入
            driver.start_session(desired_capabilities)
        except Exception as e:
            print(e)
        return driver

