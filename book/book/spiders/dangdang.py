# -*- coding: utf-8 -*-
import scrapy
from scrapy_redis.spiders import RedisSpider
from copy import deepcopy
import re
import urllib
# from ..items import DangdangItem


class DangdangSpider(RedisSpider):
    name = 'dangdang'
    allowed_domains = ['dangdang.com']
    # start_urls = ['http://book.dangdang.com/']
    redis_key = 'dangdang'

    def parse(self, response):
        # 大分类
        div_list = response.xpath("//div[@class='con flq_body']/div")

        for div in div_list:
            item = {}
            item["b_cate"] = div.xpath("./dl/dt//text()").extract()
            item["b_cate"] = [i.strip() for i in item["b_cate"] if len(i.strip()) > 0]

            item['b_cate'] = [i.strip() for i in item['b_cate'] if len(i.strip()) > 0]

            # 中间分类
            dl_list = div.xpath(".//dl[@class='inner_dl']")
            # print(dl_list)
            for dl in dl_list:
                item['m_cate'] = dl.xpath("./dt//text()").extract()
                item['m_cate'] = [i.strip() for i in item['m_cate'] if len(i.strip()) > 0]

                # 小分类
                a_list = dl.xpath("./dd/a")
                for a in a_list:
                    item['s_cate'] = a.xpath("./@title").extract_first()
                    item['s_href'] = a.xpath("./@href").extract_first()
                    if item['s_href'] is not None:
                        yield scrapy.Request(
                            item['s_href'],
                            callback=self.parse_book_list,
                            meta={'item': deepcopy(item)}
                        )

    def parse_book_list(self, response):
        item = response.meta['item']

        li_list = response.xpath("//ul[@class='bigimg']/li")

        for li in li_list:
            item['book_img'] = li.xpath("./a[@class='pic']/img/@src").extract_first()
            if item['book_img'] == "images/model/guan/url_none.png":
                item['book_img'] = li.xpath("./a[@class='pic']/img/@data-original").extract_first()
            item['book_name'] = li.xpath("./p[@name='title']/a/@title").extract_first()
            item['book_price'] = li.xpath(".//span[@class='search_now_price']/text()").extract_first()
            item['book_author'] = li.xpath(".//a[@name='itemlist-author']/@title").extract_first()
            item['book_publish_date'] = li.xpath(".//p[@class='search_book_author']/span[2]/text()").extract_first()
            if item['book_publish_date'] is not None:
            #     item['book_publish_date'] = li.xpath(".//p[@class='search_book_author']/span[2]/text()").extract_first()
            #     # 去除 /
                item['book_publish_date'] = re.sub(' /', '', item['book_publish_date'])
            #     item['book_publish_date'] = re.sub(' ', '', item['book_publish_date'])
            # 出版社
            item['book_press'] = li.xpath(".//a[@name='P_cbs']/@title").extract_first()
            item['book_detail'] = li.xpath(".//p[@class='detail']/text()").extract_first()
            print(item)

        next_url = response.xpath("//li[@class='next']/a/@href").extract_first()

        if next_url is not None:
            next_url = urllib.parse.urljoin(response.url, next_url)

            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={'item': item}
            )


