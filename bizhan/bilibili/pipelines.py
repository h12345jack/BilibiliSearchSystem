# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os

import requests

from scrapy.utils.project import get_project_settings
from scrapy.exceptions import DropItem


class ValidatePipeline(object):
    '''验证结果，并且更新数据库信息'''
    def process_item(self, item, spider):
        if not item.get('cid'):
            raise DropItem('cid is wrong %s'%item)
            return None

        if not item.get('aid'):
            raise DropItem('aid is wrong %s'%item)
            return None
        return item

    def update_mysqldb(self,cid):
        pass

class XMLDownloadPipline(object):
    '''下载 xml文件'''
    def process_item(self, item, spider):
        cid = item["cid"]
        url = "http://comment.bilibili.com/{}.xml".format(cid)
        filename = cid + '.xml'
        settings = get_project_settings()
        xml_dir = settings["XML_DIR"]

        if not os.path.exists(xml_dir):
            os.mkdir(xml_dir)
        
        fpath = os.path.join(xml_dir,filename)
        with open(fpath, 'w') as f:
            f.write(requests.get(url).content)

        return item

class JsonWriterPipeline(object):
    '''写出到文本中，便于检查和调试'''
    def __init__(self):
        self.file = open('items.jl', 'a')

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


