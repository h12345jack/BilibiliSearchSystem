#coding=utf8

import re
import json
import time
from collections import defaultdict
import os
import codecs

import MySQLdb
import lxml.html 
from lxml import etree
from settings import MYSQL_CONFIG,XML_DIR,METADATA_DIR



def __init_mysql_connection():

    host = MYSQL_CONFIG["HOST"]
    user = MYSQL_CONFIG["USERNAME"]
    password = MYSQL_CONFIG["PASSWORD"]
    db = MYSQL_CONFIG["DBNAME"]

    connection = MySQLdb.connect(host, user, password, db)
    cursor = connection.cursor()
    connection .set_character_set('utf8')
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    return cursor,connection

def __mysql_query(sql):

    cursor,connection = __init_mysql_connection()
    cursor.execute(sql)
    results = cursor.fetchall()
    cursor.close()
    connection.close()
    return results

def htt1():
    sql = "SELECT tag_list FROM video_info;"
    results = __mysql_query(sql)
    tag_list = defaultdict(int)
    rs_f = file("htt1.txt",'w')
    for tag in results:
        ele = lxml.html.fromstring(tag[0].decode("utf8"))
        href_xpath = '//a[@class="tag-val"]/@href'
        title_xpath = '////a[@class="tag-val"]/@title'
        for href,title in zip(ele.xpath(href_xpath),ele.xpath(title_xpath)):
            tag_list[title] +=1
    sort_tag_list = sorted(tag_list.items(),key=lambda x:x[1],reverse=True)
    print>>rs_f, "*"*80
    print len(sort_tag_list)
    print sort_tag_list[0][0],sort_tag_list[0][1]
    print sort_tag_list[-1][0],sort_tag_list[-1][1]
    for i in sort_tag_list:
        print>>rs_f,i[0].encode('utf8'),i[1]

    htt_list = [u"黄",u"婷",u'HTT',u'阔太太',u"阔",u"芳",u'kotete',u'w队',u"奉贤",u"李芳",
            u"阔太太",u"豆豆",u"顶顶"
            ]

    for index,i in enumerate(sort_tag_list): 
        word = i[0]
        flag = 0
        for htt in htt_list:
            if word.find(htt)!=-1:
                flag = 1
                break
        if flag:
            print index,word


def video_len_query(fname):
    filename = os.path.join(METADATA_DIR, fname)
    with open(filename) as f:
        content = f.read()
        m = re.search(r'\<timelength\>([0-9]+)\<\/timelength\>',content)
        if m:
            return m.group(1)
        else:
            raise Exception("video info wrong",filename)

def danmu():
    f_list = os.listdir(XML_DIR)
    rs_f = file("danmu.txt",'w')
    rs_f2 =file("danmu_stat.txt",'w')
    for fname in f_list:
        filename = os.path.join(XML_DIR, fname)
        with codecs.open(filename, 'r', 'utf8') as f:
            content = f.read()
            try:
                video_len = video_len_query(fname)

                node = etree.XML(content.encode('utf8'))
                danmu_xpath = "//d/text()"
                danmu_p_xpath = '//d/@p'
                max_limit_xpath = "//maxlimit/text()"
                max_limit = node.xpath(max_limit_xpath)
                assert len(max_limit) == 1,'max_limit is wrong '+ fname
                max_limit = max_limit[0]
                for p,danmu in zip(node.xpath(danmu_p_xpath),node.xpath(danmu_xpath)):
                    sentence = danmu.strip()
                    if len(sentence) > 0:
                        print>>rs_f, sentence.encode("utf8"),video_len,p
                        print>>rs_f2, len(sentence),",",video_len,",",p        
            except etree.XMLSyntaxError, e:
                try:
                    m2 = re.search(r'\<maxlimit\>([0-9]+)\<\/maxlimit\>', content)
                    if m2:
                        max_limit = m2.group(1)
                        m = re.findall(r'p\=\"(?P<p_value>.*?)\".*\>(?P<text_value>.*?)\<\/d\>', content)
                        if len(m)>0:
                            for i in m:
                                sentence = i[1]
                                p = i[0]
                                print>>rs_f,sentence.encode("utf8"),video_len,p
                                print>>rs_f2, len(sentence),",",video_len,",",p        
                except Exception as e:
                    raise e
            except Exception,e:
                print e

if __name__ == '__main__':
    danmu()
