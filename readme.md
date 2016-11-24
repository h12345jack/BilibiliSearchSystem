# 本作业主要是研究弹幕的特点
首先是完成信息分析与设计的作业，该作业需要完成一个检索系统。
我完成的是一个弹幕检索系统，而对于一个检索系统而言，首先是对于数据的获取，这部分通常使用爬虫进行抓取，事实上，如果Bilibili能够提供更好的api，显然是更容易的，但是还是习惯于传统的爬取工作，因此本项目是B站的爬虫系统。
由于B站视频数量比较多，涉及的范围也比较广，不同的视频类型之间有不同是弹幕风格。
为了进一步的细化题目，并且分析自己相对比较了解的部分。本文主要抓取了[snh48-黄婷婷](http://weibo.com/u/3668822213)相关,可能会进一步的包括SNH48 TEAM NII的部分。

<center>![](http://ww4.sinaimg.cn/mw690/006qvUVIjw1f2b43pt6paj30by0bjjs2.jpg)</center>

由于整个项目是大学四年的一次大作业，我相对比较重视，因此，整个系统的设计和系统的一些完成工作是十分重要的。

## 爬虫部分：
### 检索字段

http://search.bilibili.com/

Bilibili的检索关键词字段包括
```html
<li data-value="all">综合</li>
<li data-value="video">视频</li>
<li data-value="bangumi">番剧</li>
<li data-value="tvplay">影视</li>
<li data-value="live">直播</li>
<li data-value="special">专题</li>
<li data-value="topic">话题</li>
<li data-value="upuser">UP主</li>
<li data-value="drawyoo">画友</li>
```
由此可以看出，如果检索字段包括多个部分，如综合，视频等，可以检索不同的字段
因此除了综合检索外，为了检索的完全性，我还使用了专题和话题集合的方式进行抓取。
例如

http://www.bilibili.com/sp/%E9%BB%84%E5%A9%B7%E5%A9%B7

其包含了视频中包含TAG的href，然后将这个href放到需要抓取的url表中，
```SQL
INSERT IGNORE INTO need_crawl_url(aid,url,create_time) SELECT aid,video_url,crawler_time FROM query_table;
```
然后```python run_spider.py```便能够实现第一轮抓取，进一步的将人工筛选的query_tag进行query进一步得到query_table的数据，然后再将query_table放到need_crawl_url的表中，再启动爬虫，从need_crawl_url中抓取。可以循环进行，但是在本次项目中，最后的部分，应该包括如下：

1. sp:黄婷婷
2. query_word: 黄婷婷
3. query_word: 人工筛选其他的表达黄婷婷的单词
4. 

### 视频数据
事实上，开始的抓取的部分是没有视频的元数据的，而只有UCG的数据。这对于项目而言有巨大的打击。
因此我需要包含我抓取的视频的元数据的信息，这个部分是需要进行解析地址的。
而我参看了[哔哩哔哩真实视频地址解析-初探](#citation)和[you-get](#citation)的bilibili部分，使用了其包含的APPKEY和编码方法。
大体上获取了元数据的信息。timelength是该元素最重要的信息，是以0.001s为单位的时间信息。

### 爬虫思路
写一个获取要抓取的url列表，放在数据库中。
scrapy爬虫从数据库中读取需要抓取的url，并且将这个url放到start_urls列表中，开始抓取。

### 爬虫框架
本次爬虫的部分的框架Scrapy图为
![](http://ww2.sinaimg.cn/large/006C73MUjw1fa2642jsg5j30jg0dq40c.jpg)

而在我的具体的实现的过程中。

### url列表的获取办法：
1. query
2. 基于up主
3. 基于排行榜
4. 其他

### 数据库结构

```SQL
create database XFS_DB charset=utf8;

create table query_table(
    aid int primary key,
    query_word char(100) not null, 
    page_num int,
    video_url varchar(1000),
    crawler_time int,
    video_matrix varchar(10000)
) charset=utf8;

create table need_crawl_url(
    aid int primary key,
    url varchar(1000),
    create_time int,
    finished_time int default 0
)charset=utf8;

```

## 数据分析

首先需要对于xml文件进行一定程度的解读
```
<?xml version="1.0" encoding="UTF-8"?>
<i><chatserver>chat.bilibili.com</chatserver><chatid>9728464</chatid><mission>0</mission><maxlimit>1000</maxlimit><source>e-r</source><ds>2367399877</ds><de>2367399877</de><max_count>1000</max_count>
<d p="241.298,5,25,16707842,1472831971,0,5d2ce950,2367399877">啊黄的泪颜我来承包</d>
</i>
```
在上述的例子中,根据相关网站[弹幕信息](#citation)。
<d>标签确定了一个弹幕信息，text部分显然是数据
第一项是弹幕所在时间，单位为秒。
第二项是弹幕类型，其中:

1.  1~3 为滚动弹幕

2.  4 为底端弹幕

3.  5 为顶端弹幕

4.  6 为逆向弹幕

5.  7 为精确弹幕

6.  8 为高级弹幕。

第三项是弹幕字体大小，其中 25 为中，18 为小。

第四项是弹幕颜色，格式是十进制的 RGB 颜色。

第五项是弹幕的发送时间，使用的是 Unix 时间戳。

第六项是弹幕池，其中 0 为普通弹幕，1 为字幕弹幕，2 为特殊弹幕。

第七项是发送者的 ID 的 CRC32b 加密，可以用来屏蔽发送者。详细参考

第八项是弹幕在数据库的 ID ，可能是用于历史弹幕。

有上面的解析，可以看出，讨论分析的部分包括：弹幕随着视频出现的时间的分布情况，弹幕类型的占比情况，颜色，发送的时间相比视频的上传时间等分析。


### 统计信息
有多少个视频
这些视频的子视频切分情况
这些视频的UP主的信息是怎么样的
这些视频的view,danmaku,reply,favorite,coin,share的情况是怎么样的分布

弹幕的分布情况，类型，颜色

弹幕的文本分析，朴素贝叶斯分类器
弹幕文本情感识别 (需要相关预料信息)


### 可视化
首先可视化一个snh48总选的html页面？
然后选择一个人


### 机器学习

## 检索系统

## 网站建设

计划使用Flask进行网站建设

### 可视化部分

### 检索页面 
检索使用的工具是[Whoosh](https://pypi.python.org/pypi/Whoosh/)
该检索工具包含了全文检索，
检索包括：评论信息、弹幕检索
返回检索结果。

### 其他
之前一直遇到“OperationalError (2006, 'MySQL server has gone away')”的错误，改了很多方法，包括
[SQLAlchemy error MySQL server has gone away](http://stackoverflow.com/questions/16341911/sqlalchemy-error-mysql-server-has-gone-away)
[avoiding-mysql-server-has-gone-away-on-infrequently-used-python-flask-server](http://stackoverflow.com/questions/6471549/avoiding-mysql-server-has-gone-away-on-infrequently-used-python-flask-server)最后却是MYSQL的设置的问题导致的超时。
[Error 2006: “MySQL server has gone away” using Python, Bottle Microframework and Apache](http://stackoverflow.com/questions/12444272/error-2006-mysql-server-has-gone-away-using-python-bottle-microframework-and)

关于数据结构问题，确实存在冗余，但是为了更简单一些后面的处理，容纳这些数据的冗余的问题。

#<span id="#citation">参考信息</span>
[1].[弹幕信息](https://lintmx.com/bi-li-bi-li-dan-mu-fen-xi/):https://lintmx.com/bi-li-bi-li-dan-mu-fen-xi/
[2]. [哔哩哔哩真实视频地址解析-初探](http://blog.csdn.net/qyvlik/article/details/49473489)