#coding=utf8


import scrapy
import scrapy.cmdline

spider_name = "biliSpider"

def main():
    scrapy.cmdline.execute(argv=['scrapy', 'crawl', spider_name])


if __name__ == '__main__':
    main()
