#coding=utf8


import os
import codecs

from whoosh import index
from whoosh.fields import Schema, TEXT,ID
from whoosh.index import create_in,open_dir
import jieba
from lxml import etree
from whoosh.qparser import QueryParser

XML_DIR = 'xml_dir'
INDEX_DIR = 'index_dir'

def index():
    f_list = os.listdir(XML_DIR)
    schema = Schema(path=ID(stored=True), content=TEXT(stored=True))
    
    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)

    ix = create_in(INDEX_DIR, schema)
    
    writer = ix.writer()
    for fname in f_list:
        filename = os.path.join(XML_DIR,fname)
        with codecs.open(filename,'r','utf8') as f:
            content = f.read()
            try:
                node = etree.XML(content.encode('utf8'))
                danmu_xpath = "//d/text()"
                text_list = []
                for danmu in node.xpath(danmu_xpath):
                    word_list = jieba.cut(danmu.strip())
                    sentence = " ".join([w for w in word_list])
                    text_list.append(sentence)
                text_value = " ".join(text_list)
                if len(text_value) > 0:
                    writer.add_document(path=fname.decode('utf8'),
                                    content=text_value)
            except Exception,e:
                print filename
                print e
    writer.commit()

def query():
    if not os.path.exists(INDEX_DIR):
        os.mkdir(INDEX_DIR)

    ix = open_dir(INDEX_DIR)
    print ix
    with ix.searcher() as searcher:
        query = QueryParser("content", ix.schema).parse(u"卡黄 马鹿")
        results = searcher.search(query,limit=50)
        print results
        for e in results[:5]:
            print e["content"].encode("utf8")
            print "from",e["path"]
            print '*'*100
    ix.close()

if __name__ == '__main__':
    # index()
    query()