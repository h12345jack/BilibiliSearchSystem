# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
import re
import logging
import time
import hashlib

import requests

from sqlalchemy.orm import sessionmaker
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import DropItem
from models import db_connect,Videos,create_video_info_table


class ValidatePipeline(object):

    '''验证结果，并且更新数据库信息'''

    def process_item(self, item, spider):
        if not item.get('cid'):
            raise DropItem('cid is wrong %s' % item)
            return None

        if not item.get('aid'):
            raise DropItem('aid is wrong %s' % item)
            return None
        return item

    def update_mysqldb(self, cid):
        pass

class CommentsDownloadPipline(object):

    '''评论信息下载'''

    def process_item(self,item,spider):
        aid = item["aid"]
        filename = aid + '.json'
        settings = get_project_settings()
        comments_dir = settings["COMMNETS_DIR"] 
        if not os.path.exists(comments_dir):
            os.mkdir(comments_dir)

        fpath = os.path.join(comments_dir, filename)
        if not os.path.exists(fpath):
            data = self.Comments_content(aid)
            with open(fpath,'w') as f:
                f.write(data)

        return item


    def Comments_content(self,aid):
        data = []
        url = ("http://api.bilibili.com/x/v2/reply?"
               "jsonp=jsonp&type=1&sort=0&oid={}&pn=1&nohot=1").format(aid)
        content = requests.get(url).content
        data.append(content)
        json_data = json.loads(content)

        counts = json_data["data"]["page"]["count"]
        size = json_data["data"]["page"]["size"]
        num = int(int(counts)*1.0/int(size))

        for pn in range(2, num+1):
            url = ("http://api.bilibili.com/x/v2/reply?"
                   "jsonp=jsonp&type=1&sort=0"
                   "&oid={}&pn={}&nohot=1").format(aid, pn)
            content = requests.get(url).content
            data.append(content)
        return json.dumps(data)



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

        fpath = os.path.join(xml_dir, filename)
        with open(fpath, 'w') as f:
            f.write(requests.get(url).content)

        metadata_dir =settings["METADATA_DIR"]

        if not os.path.exists(metadata_dir):
            os.mkdir(metadata_dir)

        appkey = settings['APPKEY']
        SECRETKEY_MINILOADER = settings["SECRETKEY_MINILOADER"]
        sign_this = hashlib.md5('cid={cid}&player=1{SECRETKEY_MINILOADER}'.format(cid = cid, SECRETKEY_MINILOADER = SECRETKEY_MINILOADER)).hexdigest()
        url = 'http://interface.bilibili.com/playurl?&cid=' + cid + '&player=1' + '&sign=' + sign_this
        
        fpath = os.path.join(metadata_dir,filename)
        with open(fpath,'w') as f:
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

class MySQLWriterPipeline(object):

    def __init__(self):
        self.engine = db_connect()
        self.Session = sessionmaker(bind=self.engine)
        create_video_info_table(self.engine)
    
    def process_item(self, item, spider):
        m = re.findall(r"[0-9]+",item["url"])
        item['k_id'] = '_'.join(m)
        
        instance = Videos(**item)

        session = self.Session()

        try:
            session.merge(instance)
            session.commit()
        except Exception as e:
            session.rollback()
            logging.info(e)
        else:
            logging.info('news pipe %s' % item.get('k_id'))
        finally:
            session.close()

        aid = item["aid"]
        sql = "update need_crawl_url SET finished_time="+str(time.time())
        sql = sql + ' where aid='+aid
        
        connection = self.engine.connect()
        connection.execute(sql)
        connection.close()

        return item

    # def __del__(self):
    #     self.session.close()

        
