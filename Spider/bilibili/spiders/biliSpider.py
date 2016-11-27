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

    def __init_mysql_connection(self, *args, **kwargs):
        settings = get_project_settings()
        host = settings["MYSQL_CONFIG"]["HOST"]
        user = settings["MYSQL_CONFIG"]["USERNAME"]
        password = settings["MYSQL_CONFIG"]["PASSWORD"]
        db = settings["MYSQL_CONFIG"]["DBNAME"]

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
        now = int(time.time())
        sql = "select url from need_crawl_url where {}-finished_time > 60*60*24*30".format(now)
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        if len(results) > 0:
            for i in results:
                self.start_urls.append(i[0])
        

    def __init__(self, *args, **kwargs):
        self.__init_mysql_connection()
        self.__init_start_urls()

    def parse(self, response):
        sel = Selector(response)
        plist_xpath = '//div[@id="plist"]//option/@value'
        plist_sel = sel.xpath(plist_xpath).extract()

        if len(plist_sel) > 1:
            for url in plist_sel:
                if url.find("http://www.bilibili.com/") == -1:
                    url = "http://www.bilibili.com/" + url
                yield scrapy.Request(url, callback=self.parse_item)
        else:
            yield self.parse_item(response)

    def parse_item(self, response):

        print "*"*20, response.url
        sel = Selector(response)
        item = BilibiliItem()

        item["url"] = response.url
        item["crawl_time"] = int(time.time())
        item["title"] = ''.join(sel.xpath("//title/text()").extract())
        item["keywords"] = ''.join(
            sel.xpath('//meta[@name="keywords"]/@content').extract())
        item["description"] = ''.join(
            sel.xpath('//meta[@name="description"]/@content').extract())
        item["author"] = ''.join(
            sel.xpath('//meta[@name="author"]/@content').extract())
        item["cover_image"] = ''.join(
            sel.xpath('//img[@class="cover_image"]/@src').extract())
        item["h_title"] = ''.join(sel.xpath('//h1/@title').extract())
        item["startDate"] = ''.join(
            sel.xpath('//time[@itemprop="startDate"]/@datetime').extract())
        item["info"] = self.extract_info(sel)
        item["upinfo"] = self.extract_upinfo(sel)
        item["video_info"] = self.extract_video_info(sel)
        item["tag_list"] = self.extract_tag_list(sel)
        # cid aid
        m = re.findall(r"cid=([0-9]+)\&aid=([0-9]+)", response.body)
        print m
        if len(m) == 1:
            item["cid"] = m[0][0]
            item["aid"] = m[0][1]
            item["stats"] = self.extract_stats(sel, item["aid"], item)
            json_data = json.loads(item["stats"])
            if "data" in json_data:
                json_data2 = json_data["data"]
                item["view"] = json_data2["view"]
                item["danmaku"] = json_data2["danmaku"]
                item["reply"] = json_data2["reply"]
                item["favorite"] = json_data2["favorite"]
                item["coin"] = json_data2["coin"]
                item["share"] = json_data2["share"]
        else:
            print response.url,"cid wrong"

        return item

    def remove_space(self, raw_data):
        data = raw_data.replace("\t", '')
        data = data.replace("\n", '')
        data = data.replace("  ", "")
        return data

    def extract_info(self, sel):
        cleaner = clean.Cleaner(scripts=True,
                                javascript=True,
                                safe_attrs_only=True,
                                safe_attrs=["class", "href", "src", "title",
                                            "rel", "property", "typeof"
                                            ],
                                links=False
                                )
        info_xpath = '//div[@class="info"]'
        content = ''.join(sel.xpath(info_xpath).extract())
        clean_data = cleaner.clean_html(lxml.html.fromstring(content))
        data = lxml.html.tostring(clean_data, encoding="utf8")
        return self.remove_space(data)

    def extract_upinfo(self, sel):
        upinfo_xpath = '//div[@class="upinfo"]'
        cleaner = clean.Cleaner(scripts=True,
                                javascript=True,
                                safe_attrs_only=True,
                                safe_attrs=["class", "href", "src", "card",
                                            "mid", "title"
                                            ],
                                links=False
                                )
        content = ''.join(sel.xpath(upinfo_xpath).extract())
        clean_data = cleaner.clean_html(lxml.html.fromstring(content))
        data = lxml.html.tostring(clean_data, encoding="utf8")
        return self.remove_space(data)

    def extract_video_info(self, sel):
        video_info_xpath = '//div[@itemprop="video"]'
        data = ''.join(sel.xpath(video_info_xpath).extract())
        return self.remove_space(data)

    def extract_tag_list(self, sel):
        tag_list_xpath = '//div[@class="v_info"]'
        data = ''.join(sel.xpath(tag_list_xpath).extract())
        return self.remove_space(data)

    def extract_stats(self, sel, aid, item):
        settings = get_project_settings()
        url = ("http://api.bilibili.com/archive_stat/stat"
               "?&aid={}&type=jsonp").format(aid)
        content = requests.get(url).content
        return content
