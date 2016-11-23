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
        Session = sessionmaker(bind=self.engine)
        create_video_info_table(self.engine)
        self.session = Session()
    
    def process_item(self, item, spider):
        m = re.findall(r"[0-9]+",item["url"])
        item['k_id'] = '_'.join(m)
        instance = Videos(**item)
        
        self.session.merge(instance)

        try:
            self.session.commit()
        except InvalidRequestError as e:
            self.session.rollback()
            logging.info(e)
        except IntegrityError as e:
            self.session.rollback()
            # logging.debug(e)
        except Exception as e:
            self.session.rollback()
            logging.info(e)
        else:
            logging.info('news pipe %s' % item.get('k_id'))
            return item
        aid = item["aid"]
        sql = "update need_crawl_url SET finished_time="+str(time.time())
        sql = sql + ' where aid='+aid
        connection = self.engine.connect()
        connection.execute(sql)
        
