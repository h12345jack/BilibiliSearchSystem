#coding=utf8

import re
import json
import time
from collections import defaultdict

import MySQLdb
import lxml.html 

from settings import MYSQL_CONFIG

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




if __name__ == '__main__':
    htt1()
