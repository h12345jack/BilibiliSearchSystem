# coding=utf8

import re
import json
import time
import logging
import os
import random
import codecs
import HTMLParser
import hashlib

import MySQLdb
import lxml.html as ET
import lxml
import requests
from lxml.html import clean
from lxml import etree
from const import HEADERS, HTT_QUERY, APPKEY,SECRETKEY_MINILOADER
from const import DEFAULT_SQL, MYSQL_CONFIG
from const import XML_DIR, METADATA_DIR, COMMNETS_DIR


QUERY_HTML = 'query_keyword'
QUERY_SP = "query_sp"

logging.basicConfig(level=logging.DEBUG,
                    format=('%(asctime)s %(filename)s[line:%(lineno)d] '
                            '%(levelname)s %(message)s'),
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename='./video.log',
                    filemode='w')
def mysql_init():
    connection = MySQLdb.connect(
                 host = MYSQL_CONFIG['HOST'],
                 user = MYSQL_CONFIG['USER'],
                 passwd = MYSQL_CONFIG['PASSWORD'],
                 db = MYSQL_CONFIG['DATABASE']
                )
    cursor = connection.cursor()
    connection.set_character_set('utf8')
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    cursor.execute(DEFAULT_SQL)
    connection.commit()
    cursor.close()
    connection.close()


def mysql_cursor():
    connection = MySQLdb.connect(
                 host = MYSQL_CONFIG['HOST'],
                 user = MYSQL_CONFIG['USER'],
                 passwd = MYSQL_CONFIG['PASSWORD'],
                 db = MYSQL_CONFIG['DATABASE']
                )
    cursor = connection.cursor()
    connection.set_character_set('utf8')
    cursor.execute('SET NAMES utf8;')
    cursor.execute('SET CHARACTER SET utf8;')
    cursor.execute('SET character_set_connection=utf8;')
    return cursor, connection


def insert2json(html, query_word, page_num):
    li_xpath = '//ul[@class="ajax-render"]/li'
    cleaner = clean.Cleaner(scripts=True,
                            javascript=True,
                            safe_attrs_only=True,
                            safe_attrs=["src", "href"],
                            links=False
                            )

    video_url_xpath = './a/@href'
    filename = query_word+'_'+str(page_num)+'.jsonline'

    filepath = os.path.join(QUERY_HTML, filename)

    print filepath
    

    with open(filepath, 'w') as output:

        for ele in html.xpath(li_xpath):
            data = dict()

            data["video_url"] = ''.join(ele.xpath(video_url_xpath))
            data["crawler_time"] = int(time.time())
            data["query_word"] = query_word
            data["page_num"] = page_num

            video_matrix = lxml.html.tostring(cleaner.clean_html(ele),
                                              encoding="utf8")

            video_matrix = video_matrix.replace("\n", '')
            data["video_matrix"] = video_matrix.replace("\t", '')
            output.write(json.dumps(data)+"\n")

    #插入数据库，关闭相关资源
    cursor,connection = mysql_cursor()
    insert2mysql(filepath,cursor,connection)
    cursor.close()
    connection.close()

def insert2mysql(fpath,cursor,connection):
    with codecs.open(fpath,'r','utf8') as f:
        for lj in f.readlines():
            json_data = json.loads(lj.strip())
            json_data["aid"] = "".join(re.findall(r'av([0-9]*)',json_data["video_url"]))
            sql = "INSERT INTO query_table("
            sql += ",".join(json_data.keys())
            sql += ")values("
            sql += ",".join(["%s" for i in json_data.keys()])+");"
            try:
                cursor.execute(sql,json_data.values())
                connection.commit()
            except  MySQLdb.Error,e:
                if not str(e.args[0]) == "1062":
                   logging.warning("MySQL Error [%d]: %s" % (e.args[0], e.args[1]))




def crawler_keyword(keyword):
    '''
    给出一个关键词，爬取
    '''
    if not os.path.exists(QUERY_HTML):
        os.mkdir(QUERY_HTML)

    url = 'http://search.bilibili.com/all?keyword='
    query_url = url + keyword.encode("utf8").strip()
    print query_url
    content = requests.get(query_url, headers=HEADERS).content
    html = ET.fromstring(content.decode("utf8"))
    num_pages_xpath = '//body/@data-num_pages'
    num_pages = html.xpath(num_pages_xpath)
    assert len(num_pages) == 1, "num_pages is NULL"
    insert2json(html, keyword, 1)

    for page in range(2, int(num_pages[0])+1):
        query_url = url + keyword.strip() + "&page=" + str(page)
        print query_url
        try:
            content = requests.get(query_url, headers=HEADERS).content
            html = ET.fromstring(content.decode("utf8"))
            insert2json(html, keyword, page)
            time.sleep(random.random())
        except Exception as e:
            logging.debug(e)



def crawler_special(keyword):
    '''
    给出一个special进行检索
    '''
    if not os.path.exists(QUERY_SP):
        os.mkdir(QUERY_SP)

    url = "http://www.bilibili.com/sp/"
    query_url = url + keyword.encode('utf8').strip()
    content = requests.get(query_url, headers=HEADERS).content
    spid = re.findall(r'var spid\s?=\s?\"(.*?)\"', content)
    assert len(spid) == 1, "spid is NULL"
    spid = spid[0]

    tag_url = "http://www.bilibili.com/sppage/tag-hot-{}-1.html".format(spid)
    content = requests.get(tag_url, headers=HEADERS).content
    html = lxml.html.fromstring(content)
    end_page = html.xpath('//*[@class="p endPage"]/text()')
    assert len(end_page) == 1, "end_page is NULL"

    for page in range(1, int(end_page[0])+1):
        tag_url = "http://www.bilibili.com/sppage/tag-hot-{}-{}.html".format(
            spid, page)
        logging.info(tag_url)

        content = requests.get(tag_url, headers=HEADERS).content
        filename = keyword + "_" + str(page)+'.html'
        file_path = os.path.join(QUERY_SP, filename)
        with open(file_path, "w") as f:
            f.write(content)


def extract_url_from_sp():
    sp_f = file("sp_url.sql",'w')
    print>>sp_f,"USE XFS_DB;"
    f_list = [os.path.join(QUERY_SP,i) for i in os.listdir(QUERY_SP)]
    for fname in f_list:
        with codecs.open(fname) as f:
            html = lxml.html.fromstring(f.read())
            href_xpath = '//div[@class="v"]/a/@href'
            for href in html.xpath(href_xpath):
                if href.find("http://www.bilibili.com") == -1:
                    href = "http://www.bilibili.com" + href
                aid = "".join(re.findall(r'av([0-9]*)',href))
                sql = ('INSERT IGNORE INTO need_crawl_url(aid,url,create_time)'
                      'VALUES("{}","{}","{}");')\
                      .format(aid,href,int(time.time()),int(time.time()))
                print>>sp_f,sql
    print>>sp_f,"INSERT IGNORE INTO need_crawl_url(aid,url,create_time) SELECT aid,video_url,crawler_time FROM query_table;"   
    print 'sp_url.sql compelete!'


def download_img():
    '''
    纯个人爱好问题，然后上传到微博。
    '''
    f_list = [os.path.join(QUERY_SP, i) for i in os.listdir(QUERY_SP)]
    for filename in f_list:
        with open(filename, 'r') as f:
            content = f.read()
            html = lxml.html.fromstring(content)
            for i in html.xpath("//li//img/@src"):
                img_fname = i[i.rfind("/")+1:]
                img_fname = os.path.join("img", img_fname)
                with open(img_fname, 'wb') as img_f:
                    img_f.write(requests.get(i).content)
                print img_fname, ' download!'

def downnload_sp_xml():
    xml_url = "http://www.bilibili.com/sitemap/sp.xml"
    with open("sp.xml",'w') as f:
        content = requests.get(xml_url).content
        f.write(content)
        root = etree.XML(content)
        html_parser = HTMLParser.HTMLParser()
        namespace = {'g':"http://www.google.com/schemas/sitemap/0.84"}
        import urllib
        for i in root.xpath("//g:loc/text()",namespaces=namespace):
            print urllib.unquote(i)


def xml_downloader(cid):
    url = "http://comment.bilibili.com/{}.xml".format(cid)
    filename = cid + '.xml'
    xml_dir = XML_DIR

    if not os.path.exists(xml_dir):
        os.mkdir(xml_dir)

    fpath = os.path.join(xml_dir, filename)
    with open(fpath, 'w') as f:
        f.write(requests.get(url).content)
    print fpath

    metadata_dir = METADATA_DIR

    if not os.path.exists(metadata_dir):
        os.mkdir(metadata_dir)

    appkey = APPKEY
    sign_this = hashlib.md5('cid={cid}&player=1{SECRETKEY_MINILOADER}'.format(cid = cid, SECRETKEY_MINILOADER = SECRETKEY_MINILOADER)).hexdigest()
    url = 'http://interface.bilibili.com/playurl?&cid=' + cid + '&player=1' + '&sign=' + sign_this
    
    fpath = os.path.join(metadata_dir,filename)
    with open(fpath,'w') as f:
        f.write(requests.get(url).content)
    print fpath


def step1():
    keyword = [u"SNH48",u"李艺彤",u"黄婷婷"]
    for k in keyword:
        crawler_keyword(k)
    
    sp_list = [u"SNH48",u"李艺彤",u"黄婷婷"]

    for sp in keyword:
        crawler_special(sp)
    extract_url_from_sp()


def main():
    # mysql_init()
    step1()
    for k in HTT_QUERY:
        crawler_keyword(k)

if __name__ == '__main__':
   main()
