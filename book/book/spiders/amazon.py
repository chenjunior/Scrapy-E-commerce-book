# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
# from ..items import AmazonItem


class AmazonSpider(RedisCrawlSpider):
    name = 'amazon'
    allowed_domains = ['amazon.cn']
    # start_urls = ['https://www.amazon.cn/s/ref=nb_sb_noss?__mk_zh_CN=%E4%BA%9A%E9%A9%AC%E9%80%8A%E7%BD%91%E7%AB%99&url=search-alias%3Dstripbooks&field-keywords=]
    redis_key = 'amazon'

    rules = (
        # 大分类
        Rule(
            LinkExtractor(restrict_xpaths=("//ul[@class='a-unordered-list a-nostyle a-vertical s-ref-indent-one']/div/li")),
            follow=True),
        # 小分类
        Rule(
            LinkExtractor(restrict_xpaths=("//ul[@class='a-unordered-list a-nostyle a-vertical s-ref-indent-two']/div/li")),
            follow=True),
        # 匹配图书的url地址
        Rule(
            LinkExtractor(restrict_xpaths=("//div[@id='mainResults']/ul/li//h2/..")),
            callback="parse_book_detail"),
        # 匹配图书的翻页
        Rule(
            LinkExtractor(restrict_xpaths=("//div[@id='pagn']")),
            follow=True),
    )

    def parse_book_detail(self, response):
        item = {}
        item['book_title'] = response.xpath("//span[@id='ebooksProductTitle']/text()").extract()
        if item['book_title'] is not None:
            item["book_title"] = [i.strip() for i in item["book_title"] if len(i.strip()) > 0]
        item['book_press'] = response.xpath("//b[text()='出版社:']/../text()").extract_first()
        item['book_author'] = response.xpath("//span[@class='author notFaded']/a/text()").extract()
        # item["book_price"] = response.xpath("//div[@id='soldByThirdParty']/span[2]/text()").extract_first()
        item['book_price'] = response.xpath(
            "//span[@class='a-size-base a-color-price a-color-price']/text()").extract_first()
        if item['book_price'] is not None:
            item['book_price'] = response.xpath(
            "//span[@class='a-size-base a-color-price a-color-price']/text()").extract_first().strip()
        item['book_img'] = response.xpath("//div[@id='ebooks-img-canvas']/img/@src").extract_first()
        item['book_cate'] = response.xpath(
            "//div[@id='wayfinding-breadcrumbs_feature_div']/ul//a/text()").extract()
        item["book_cate"] = [i.strip() for i in item["book_cate"] if len(i.strip()) > 0]
        item["book_url"] = response.url

        # print(item)
        yield item
