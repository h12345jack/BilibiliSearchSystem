# -*- coding: utf-8 -*-


import json
import os
import time
import re

import MySQLdb
import requests
from lxml.html import clean
import lxml.html

import scrapy
import scrapy.cmdline
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

from bilibili.items import BilibiliItem

spider_name = "biliSpider"

class BilispiderSpider(scrapy.Spider):
    name = spider_name
    allowed_domains = ["bilibili.com"]
    start_urls = []

    def __init_mysql_connection(self,*args, **kwargs):
        host = 'localhost'
        user = 'root'
        password = 'admin'
        db = 'XFS_DB'
        self.connection = MySQLdb.connect(host, user, password, db)
        self.cursor = self.connection.cursor()
        self.connection .set_character_set('utf8')
        self.cursor.execute('SET NAMES utf8;')
        self.cursor.execute('SET CHARACTER SET utf8;')
        self.cursor.execute('SET character_set_connection=utf8;')

    def __del__():
        self.cursor.close()
        self.connection.close()

    def __init_start_urls(self):
        sql = "select url from need_crawl_url where finished_time = 0"
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if len(results)>0:
            for i in results:
                self.start_urls.append(i[0])


    def __init__(self, *args, **kwargs):
        self.__init_mysql_connection()
        self.__init_start_urls()
 

    def parse(self, response):
        sel = Selector(response)
        plist_xpath = '//div[@id="plist"]//option/@value'
        plist_sel = sel.xpath(plist_xpath).extract()

        if len(plist_sel)>1:
            for url in plist_sel:
                if url.find("http://www.bilibili.com/")==-1:
                    url = "http://www.bilibili.com/" + url
                yield scrapy.Request(url,callback = self.parse_item)
        else:
            self.parse_item(response)

    def parse_item(self,response):

        print "*"*20,response.url
        sel = Selector(response)
        item = BilibiliItem()

        item["url"] = response.url
        item["crawl_time"] = int(time.time())
        item["title"] = sel.xpath("//title()").extract()
        item["keywords"] = sel.xpath('//meta[@name="keywords"]').extract()
        item["description"] = sel.xpath('//meta[@name="description"]').extract()
        item["author"] = sel.xpath('//meta[@name="author"]').extract()
        item["cover_image"] = sel.xpath('//img[@class="cover_image"]').extract()
        item["h_title"] = sel.xpath('//h1/@title').extract()
        item["startDate"] = sel.xpath('//time[@itemprop="startDate"]/@datatime').extract()
        
        #cid aid
        m = re.findall(r"cid=([0-9]+?)\&([0-9]+?\&)",response.body)
        if len(m)>1:
            item["cid"] = m[0]
            item["aid"] = m[1]

        return item

 
        
    def extract_info(self,sel):
        info_xpath = '//div[@class="info"]'

    def extract_upinfo(self,sel):
        upinfo_xpath = '//div[@class="upinfo"]'

    def extract_video_info(self,sel):
        video_info_xpath = '//div[@itemprop="video"]'

    def extract_tag_list(self,sel):
        tag_list_xpath = '//div[@class="v_info"]'
        

    def extract_comments(self,sel):
        '''
        http://api.bilibili.com/x/v2/reply?jsonp=jsonp&type=1&sort=0&oid=7182953&pn=1&nohot=1
        '''
        pass

    def extract_stats(self,aid):
        settings = get_project_settings()
        headers = settings["USER_AGENT"]
        url = "http://api.bilibili.com/archive_stat/stat?&aid={}&type=jsonp".format(aid)
        content = requests.get(url,headers=headers).content
        return content
   
   

