# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import pymongo


class JDPipeline(object):

    def __init__(self):
        # 链接mysql数据库
        self.conn = pymysql.connect(
            host='localhost',
            user='root',
            password='mysql',
            database='jingdong',
            port=3306,
            charset='utf8')
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        if spider.name == 'jd':
            print(item)
            try:
                self.cursor.execute(
                    "insert into books(b_cate,s_cate,s_href,book_name,book_author,book_img,book_press,book_publish_date,book_sku,book_price) value ({},{},{},{},{},{},{},{},{},{});".format(item['b_cate'],item['s_cate'],item['s_href'],item['book_name'],item['book_author'],item['book_img'],item['book_press'],item['book_publish_date'],item['book_sku'],item['book_price']))
                self.conn.commit()
            except Exception as error:
                print(error)

        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()


class DangdangPipeline(object):
    def __init__(self):
        self.DangdangClient = pymongo.MongoClient()
        self.collention = self.DangdangClient['dangdang']['books']

    def process_item(self, item, spider):
        if spider.name == 'dangdang':
            self.collention.insert(dict(item))

        return item


class AmazonPipeline(object):
    def __init__(self):
        self.AmazonClient = pymongo.MongoClient()
        self.collention = self.AmazonClient['Amazon']['books']

    def process_item(self, item, spider):
        if spider.name == 'amazon':
            print(item)
            try:
                self.collention.insert(dict(item))
            except Exception as error:
                print(error)
        return item
