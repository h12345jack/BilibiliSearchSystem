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
from const import XML_DIR,METADATA_DIR




def video_len_query(fname):
    filename = os.path.join(METADATA_DIR, fname)
    with open(filename) as f:
        content = f.read()
        m = re.search(r'\<timelength\>([0-9]+)\<\/timelength\>',content)
        if m:
            return m.group(1)
        else:
            raise Exception("video info wrong",filename)

def danmu(cid):
    f_list = os.listdir(XML_DIR)
    rs_f = file(cid+".csv",'w')
    fname = cid + '.xml'
    filename = os.path.join(XML_DIR, fname)
    print>>rs_f,"content,video_len,show_time,cls,font_size,color,submit_time,pool,id1,id2"
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
                    print>>rs_f, sentence.encode("utf8")+','+str(float(video_len)/1000)+","+p
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
                            print>>rs_f,sentence.encode("utf8")+','+str(float(video_len)/1000)+','+p
            except Exception as e:
                raise e
        except Exception,e:
            print e

if __name__ == '__main__':
    danmu("8150643")
