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
    k_id        = Field()
    url         = Field()
    crawl_time  = Field()
    title       = Field()
    keywords    = Field()
    description = Field()
    author      = Field()
    cover_image = Field()
    h_title     = Field()
    startDate   = Field()
    cid         = Field()
    aid         = Field()
    info        = Field()
    upinfo      = Field()
    video_info  = Field()
    tag_list    = Field()
    comments    = Field()
    stats       = Field()

