# coding=utf8


import os
import codecs
import json
import re
import time

import jieba
from jieba.analyse.analyzer import ChineseAnalyzer

from lxml import etree
import lxml.html
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from whoosh import scoring
from sqlalchemy.orm import sessionmaker
from models import Videos,db_connect


XML_DIR = '../Spider/xml_dir'
INDEX_DIR = 'index_dir'
DIC_DIR = 'dictionary'

AD_DIC = 'ad.txt'
POLITICS_DIC = 'politics.txt'
SALACITY_DIC = 'salacity.txt'
STOPWORD_DIC = 'stopword.dic'


def load_stop_word():
    stop_word_path = os.path.join(DIC_DIR, STOPWORD_DIC)
    stop_word = list()
    with codecs.open(stop_word_path, 'r', 'utf8') as f:
        for i in f.readlines():
            w = i.strip()
            if len(w) > 0:
                stop_word.append(w)
    return set(stop_word)


def load_ad_word():
    ad_word_path = os.path.join(DIC_DIR, AD_DIC)
    ad_word = list()
    with codecs.open(ad_word_path, 'r', 'utf8') as f:
        for i in f.readlines():
            w = i.strip()
            if len(w) > 0:
                ad_word.append(w)
    return set(ad_word)


def load_politics_word():
    politics_word_path = os.path.join(DIC_DIR, POLITICS_DIC)
    politics_word = list()
    with codecs.open(politics_word_path, 'r', 'utf8') as f:
        for i in f.readlines():
            w = i.strip()
            if len(w) > 0:
                politics_word.append(w)
    return set(politics_word)


def load_salacity_word():
    salacity_word_path = os.path.join(DIC_DIR, SALACITY_DIC)
    salacity_word = list()
    with codecs.open(salacity_word_path) as f:
        for i in f.readlines():
            w = i.strip()
            if len(w) > 0:
                salacity_word.append(w)
    return set(salacity_word)


def load_all_words():

    filter_words = set()
    ad_word = load_ad_word()
    filter_words = filter_words | ad_word

    salacity_word = load_salacity_word()
    filter_words = filter_words | salacity_word

    politics_word = load_politics_word()
    filter_words = filter_words | politics_word

    stop_word = load_stop_word()
    filter_words = filter_words | stop_word

    return filter_words


def index():

    '''
    对于弹幕信息进行检索，如果lxml解析报错，去掉该文件将不被检索
    ''' 
    
    f_list = os.listdir(XML_DIR)
    schema = Schema(path =ID(stored=True),\
                    content=TEXT(analyzer = ChineseAnalyzer(),stored=True),\
                    radio= NUMERIC(float,stored=True)
                    )
    new_or_not = 0
    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)
        new_or_not = 1

    # if new_or_not:
    #     ix = create_in(INDEX_DIR, schema)
    # else:
    #     ix = open_dir(INDEX_DIR)

    ix = create_in(INDEX_DIR, schema)

    writer = ix.writer()

    filter_words = load_all_words()

    num = 0

    for fname in f_list:
        if fname.find(".xml")==-1:continue
        filename = os.path.join(XML_DIR, fname)
        with codecs.open(filename, 'r', 'utf8') as f:
            content = f.read()
            try:
                node = etree.XML(content.encode('utf8'))
                danmu_xpath = "//d/text()"
                text_list = []
                max_limit_xpath = "//maxlimit/text()"
                max_limit = node.xpath(max_limit_xpath)
                assert len(max_limit) == 1,'max_limit is wrong '+ fname
                max_limit = max_limit[0]
                for danmu in node.xpath(danmu_xpath):
                    sentence = danmu.strip()
                    if len(sentence) > 0:
                        text_list.append(sentence)        
                if len(text_list)>0:
                    text_value = u' \n '.join(text_list)
                    radio = len(text_list)*1.0/int(max_limit)
                    writer.add_document(path=fname.decode('utf8'),
                                        content=text_value,
                                        radio = radio
                                        )
                num = num + 1
            except etree.XMLSyntaxError, e:
                print filename,e
            except Exception,e:
                print e
    print num,'danmu indexed!'
    writer.commit()


def query(query_phrase):
    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)

    filter_words = load_all_words()
    word_list = jieba.cut(query_phrase)
    query_phrase = " ".join([w for w in word_list \
        if w not in filter_words and len(w.strip())>0])
    query_phrase = query_phrase.replace("  "," ")
    
    print type(query_phrase),query_phrase

    ix = open_dir(INDEX_DIR)

    with ix.searcher(weighting=scoring.BM25F(B=0.1)) as searcher:

        query = QueryParser("content", ix.schema).parse(query_phrase)
        results = searcher.search(query, limit=150)
        re_json = []
        for e in results:
            score = float(e.score)*float(e["radio"])
            # print e.score,e["radio"]
            m = e.highlights("content").encode('utf8')
            re_json.append((score,e["path"],m))
            # print '*'*20
        print len(re_json)
        rs = sorted(re_json,key=lambda x:x[0],reverse=True)
        res = query_output(rs)
        ix.close()
        
        return res


def query_output(rs):
    res = [] 
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    session = Session()

    for i in rs:
        data = dict()
        cid = i[1][:i[1].rfind(".xml")]
        print cid,
        value = session.query(Videos).filter(Videos.cid==cid).first()
        if value:
            data = value.as_dict()
            data["danmu"] = extract_danmu_example(i[2])
            data["score"] = i[0]
            T_index = data["startDate"].find('T')
            data["date"] = data["startDate"][:T_index]
            data["hour"] = data["startDate"][T_index+1:]
            data["tag_list"] = extract_tag(data["tag_list"])
            data["u_face"] = extract_u_face(data["upinfo"])
            data["r_info"] = extract_r_info(data["upinfo"])
            res.append(data)

    print res[0]["cid"]
    print len(res),"results find!"
    return res

def mysql_result_by_cid(cid):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    session = Session()
    data = dict()
    value = session.query(Videos).filter(Videos.cid==cid).first()
    if value:
        data = value.as_dict()
        data["danmu"] = extract_danmu_example(cid)
        T_index = data["startDate"].find('T')
        data["date"] = data["startDate"][:T_index]
        data["hour"] = data["startDate"][T_index+1:]
        data["tag_list"] = extract_tag(data["tag_list"])
        data["u_face"] = extract_u_face(data["upinfo"])
        data["r_info"] = extract_r_info(data["upinfo"])
        data["crawl_time"] = time.asctime(time.localtime(int(data["crawl_time"])))
        data["page"] = data["k_id"][data["k_id"].find("_"   )+1:]
        return data
    return []


def extract_danmu_example(danmu):
    rs = [[],[],[]]
    danmu_list = danmu.split('\n')
    for i,ele in enumerate(danmu_list[:50]):
        rs[i%3].append(ele.decode("utf8"))
    return rs

def extract_tag(tag_html):
    root = lxml.html.fromstring(tag_html)
    tag_xpath = "//li/a"
    rs = []
    for i in root.xpath(tag_xpath):
        rs.append(lxml.html.tostring(i,encoding="utf8").decode("utf8"))
    return rs

def extract_u_face(upinfo):
    m = re.findall(r"\<div\s?class=\"u\-face\"\>(.*?)\<\/div\>",upinfo)
    return ''.join(m)

def extract_r_info(upinfo):
    m = re.findall(r"\<div\s?class=\"r\-info\"\>(.*)\<\/div\><\/div\>",upinfo)
    return ''.join(m)


def main():
    print u'开始索引文件吗？确定输入1'
    config = raw_input()
    if config == '1':
        index()
    else:
        print u'取消索引操作'
        exit(-1)


if __name__ == '__main__':
    main()

