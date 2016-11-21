#coding=utf8

import requests
import chardet
import lxml.html 
import MySQLdb

def main():
    url = 'https://www.baidu.com/'
    content = requests.get(url).content
    e = lxml.html.fromstring(content)
    print type(lxml.html.tostring(e,encoding="utf8"))
    print lxml.html.tostring(e,encoding="utf8")
   

def main():
    host = 'localhost'
    user = 'root'
    password = 'admin'
    db = 'XFS_DB'
    connection = MySQLdb.connect(host, user, password, db)
    cursor = connection.cursor()
    connection .set_character_set('utf8')
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    sql = "select url from need_crawl_url where finished_time = 0"
    cursor.execute(sql)
    result = cursor.fetchall()
    print result

if __name__ == '__main__':
    main()