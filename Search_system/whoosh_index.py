# coding=utf8


import os
import codecs

import jieba
from jieba.analyse.analyzer import ChineseAnalyzer

from lxml import etree
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, NUMERIC
from whoosh.index import create_in, open_dir
from whoosh.qparser import QueryParser
from whoosh import scoring

XML_DIR = '../bizhan/xml_dir'
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
                    content=TEXT(analyzer = ChineseAnalyzer()),\
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
        results = searcher.search(query, limit=50)
        re_json = []
        for e in results[:25]:
            value = float(e.score)*float(e["radio"])
            # print e.score,e["radio"]
            # print e.highlights("content").encode('utf8')
            # print "from", e["path"]
            re_json.append((value,e["path"]))
            # print '*'*20
        ix.close()
        rs = sorted(re_json,key=lambda x:x[0],reverse=True)
        for i in rs:
            print i

        return re_json[:20]



if __name__ == '__main__':

    query(u"黄宇直")

