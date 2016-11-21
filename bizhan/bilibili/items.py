# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Field

class BilibiliItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    url = Field()
    
    crawl_time = Field()
    #【国民美少女】【黄婷婷】女汉子齐吼好汉歌_综艺_娱乐_bilibili_哔哩哔哩弹幕视频网</title>
    title = Field() ## title
    #哔哩哔哩,Bilibili,B站,弹幕,娱乐,综艺,kimotohtt,黄婷婷,SNH48,塞纳河,国民美少女
    keywords = Field() #meta name="keywords"
    #来疯 http://v.laifeng.com/62327  女汉子齐吼好汉歌" />
    description = Field() #meta name="description"
    #kimotohtt
    author = Field() #meta name="author"
    #http://i2.hdslb.com/bfs/archive/23a50dc984f065d7d89e7f684ca885b9806061a9.jpg
    cover_image = Field() # //img[@class = "cover_image"]
    #<h1 title="【国民美少女】【黄婷婷】女汉子齐吼好汉歌">【国民美少女】【黄婷婷】女汉子齐吼好汉歌</h1
    h_title = Field() #h1
    # <div class="tminfo" xmlns:v="http://rdf.data-vocabulary.org/#"><a href="/" rel="v:url" property="v:title">主页</a> &gt; <span typeof="v:Breadcrumb"><a href='/video/ent.html'  rel="v:url" property="v:title">娱乐</a></span> &gt; <span typeof="v:Breadcrumb"><a href="/video/ent-variety-1.html" class="on" rel="v:url" property="v:title">综艺</a></span>
    startDate = Field()
    #cid=6779486&aid=4195543
    cid = Field()
    aid = Field()
    info = Field() 
    upinfo = Field()
    video_info = Field()
    tag_list = Field()
    comments = Field()
    stats = Field()
    



