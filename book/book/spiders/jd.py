# -*- coding: utf-8 -*-
import scrapy
from copy import deepcopy
import json
import urllib
# from ..items import JDItem


class JdSpider(scrapy.Spider):
    name = 'jd'
    allowed_domains = ['jd.com', 'p.3.cn']
    start_urls = ['https://book.jd.com/booksort.html']

    def parse(self, response):
        # 京东图书大分类
        dt_list = response.xpath("//div[@class='mc']//dt")
        # print(dt_list)

        for dt in dt_list:
            item = {}
            # 大分类
            item['b_cate'] = dt.xpath("./a/text()").extract_first()
            # item['href'] = dt.xpath("./a/@href").extract_first()

            # em_list = response.xpath("//div[@class='mc']//em") 这种写法获取的是页面所有的em,而不是获取当前大分类下的em
            em_list = dt.xpath("./following-sibling::dd[1]//em")  # 小分类列表
            # print(em_list)
            for em in em_list:
                item['s_cate'] = em.xpath("./a/text()").extract_first()
                item['s_href'] = em.xpath("./a/@href").extract_first()
                if item['s_href'] is not None:
                    item['s_href'] = "https:" + item['s_href']
                    yield scrapy.Request(
                        item['s_href'],
                        callback=self.parse_book_list,
                        meta={'item': deepcopy(item)}

                    )

    def parse_book_list(self, response):
        """解析列表页"""
        item = response.meta['item']
        li_list = response.xpath("//div[@id='plist']/ul/li")

        for li in li_list:
            item['book_img'] = li.xpath(".//div[@class='p-img']//img/@src").extract_first()
            if item['book_img'] is None:
                item["book_img"] = li.xpath(".//div[@class='p-img']//img/@data-lazy-img").extract_first()
            item['book_img'] = "https:" + item['book_img'] if item['book_img'] is not None else None
            # strip()去除名字左右的空格
            item['book_name'] = li.xpath(".//div[@class='p-name']//em/text()").extract_first().strip()
            item['book_author'] = li.xpath(".//span[@class='author_type_1']/a/text()").extract()
            # 出版社
            item['book_press'] = li.xpath(".//span[@class='p-bi-store']/a/@title").extract_first()
            # 出版日期
            item['book_publish_date'] = li.xpath(".//span[@class='p-bi-date']/text()").extract_first().strip()
            # 因为价格是通过JS生成的,所以需要构造价格url
            item['book_sku'] = li.xpath("./div/@data-sku").extract_first()

            yield scrapy.Request(
                "https://p.3.cn/prices/mgets?skuIds={}".format(item['book_sku']),
                callback=self.parse_book_price,
                meta={'item': deepcopy(item)}
            )

        # 列表页翻页
        next_url = response.xpath("//a[@class='pn-next']/@href").extract_first()

        if next_url is not None:
            # next_url = "https:" + next_url
            next_url = urllib.parse.urljoin(response.url, next_url)
            yield scrapy.Request(
                next_url,
                callback=self.parse_book_list,
                meta={'item': item}
            )

    def parse_book_price(self, response):
        item = response.meta['item']
        item['book_price'] = json.loads(response.body.decode())[0]['op']
        yield item





