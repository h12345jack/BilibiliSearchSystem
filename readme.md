# 本作业主要是研究弹幕的特点
首先是完成信息分析与设计的作业，该作业需要完成一个检索系统。
我完成的是一个弹幕检索系统，而对于一个检索系统而言，首先是对于数据的获取，这部分通常使用爬虫进行抓取，事实上，如果Bilibili能够提供更好的api，显然是更容易的，但是还是习惯于传统的爬取工作，因此本项目是B站的爬虫系统。
由于B站视频数量比较多，涉及的范围也比较广，不同的视频类型之间有不同是弹幕风格。
为了进一步的细化题目，并且分析自己相对比较了解的部分。本文主要抓取了snh48-黄婷婷相关（应该包括SNH48 TEAM NII）的部分。
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
由此可以看出，如果检索字段包括多个，如综合，视频等，可以检索不同的字段
因此除了综合检索外，为了检索的完全性，我还使用了专题和话题集合的方式进行抓取。
http://www.bilibili.com/sp/%E9%BB%84%E5%A9%B7%E5%A9%B7

### 视频数据

### 爬虫思路
写一个获取要抓取的url列表，放在数据库中。
scrapy爬虫从数据库中读取需要抓取的url，并且将这个url放到start_urls列表中，开始抓取。

### url列表的获取办法：
1. query
2. 基于up主
3. 基于排行榜
4. 其他

### 数据库结构

```SQL
create table query_table(
    query_word char(100) not null, 
    page_num int,
    video_url varchar(1000),
    crawler_time int,
    video_matrix varchar(10000)
) charset=utf8;

create table need_crawl_url(
    url varchar(1000),
    create_time int,
    finished_time int default 0
)
```
## 数据分析

### 统计信息

### 可视化

### 机器学习

## 检索系统

## 网站建设

计划使用Flask进行网站建设

### 可视化部分

### 检索页面 
