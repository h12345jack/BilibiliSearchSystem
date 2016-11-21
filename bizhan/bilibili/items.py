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
    tminfo  = Field()
    startDate = Field()
    # <div class="v-title-info">
    #     <div class="v-title-line"><i class="b-icon b-icon-a b-icon-play" title="播放"></i><span id="dianji"></span></div>
    #     <div class="v-title-line"><i class="b-icon b-icon-a b-icon-danmaku" title="弹幕"></i><span id="dm_count"></span></div>
    #     <div class="v-title-line v-rank"><!-- 排行数据 --></div>
    #     <div class="v-title-line v-coin coin_btn"><i class="b-icon b-icon-a b-icon-coin" title="投硬币"></i><span class="coin-status">硬币</span><span id="v_ctimes"></span></div>
    #     <div class="v-title-line v-stow fav_btn"><i class="b-icon b-icon-a b-icon-stow" title="收藏"></i><span class="stow-status">收藏</span><span id="stow_count"></span></div>
    # </div>
     # <div class="usname"><a class="name" href="http://space.bilibili.com/1890733" mid="1890733" card="kimotohtt" title="kimotohtt" target="_blank">kimotohtt</a><a mid="1890733" href="http://message.bilibili.com/#whisper/mid1890733" target="_blank" class="message">私信</a>
     #                    </div>
     #                    <div class="sign">微博「@木元真実」 / SNH48-黄婷婷 推し / 演员宋轶 / 日剧日影 / 以及一切自己喜欢的想投稿的视频 以上</div>
     # <div class="up-video-message">
    #     <div>投稿：177</div>
    #     <div>粉丝：4660</div>
    # </div>   
    upinfo = Field()
    #cid=6779486&aid=4195543
    cid = Field()
    aid = Field()
     # <div itemprop="video" itemscope itemtype="http://schema.org/VideoObject" style="display:none">
    #     <meta itemprop="name" property="media:title" content="【国民美少女】【黄婷婷】女汉子齐吼好汉歌" />
    #     <span property="media:type" content="application/x-shockwave-flash">
    #         <meta itemprop="duration" content="T2M49S" />
    #         <meta itemprop="thumbnailUrl" rel="media:thumbnail" content="http://i2.hdslb.com/bfs/archive/23a50dc984f065d7d89e7f684ca885b9806061a9.jpg" />
    #         <meta itemprop="embedURL" content="http://static.hdslb.com/miniloader.swf?aid=4195543&page=1" />
    #         <meta itemprop="uploadDate" content="2016-03-26T21:11" />
    #     </span>
    # </div>
    video_info =Field()
    # <ul class="tag-list"><li><a class="tag-val" href="/tag/%E9%BB%84%E5%A9%B7%E5%A9%B7/" title="黄婷婷" target="_blank">黄婷婷</a></li><li><a class="tag-val" href="/tag/SNH48/" title="SNH48" target="_blank">SNH48</a></li><li><a class="tag-val" href="/tag/%E5%A1%9E%E7%BA%B3%E6%B2%B3/" title="塞纳河" target="_blank">塞纳河</a></li><li><a class="tag-val" href="/tag/%E5%9B%BD%E6%B0%91%E7%BE%8E%E5%B0%91%E5%A5%B3/" title="国民美少女" target="_blank">国民美少女</a></li>                                    </ul>
    tag_list = Field()



