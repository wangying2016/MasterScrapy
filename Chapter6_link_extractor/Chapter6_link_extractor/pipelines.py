# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
import mysql.connector

class PriceConverterPipeline(object):

    # 英镑兑换人民币汇率
    exchange_rate = 8.5309

    def process_item(self, item, spider):
        # 提取 item 的 price 字段
        # 去掉前面的英镑符号£，转换为 float 类型，乘以汇率
        price = float(item['price'][1:]) * self.exchange_rate

        # 保留 2 位小数，赋值回 item 的 price 字段
        item['price'] = '¥%.2f' % price

        return item


class DuplicatesPipelines(object):

    def __init__(self):
        self.book_set = set()

    def process_item(self, item, spider):
        name = item['name']
        if name in self.book_set:
            raise DropItem('Duplicate book found: %s' % item)

        self.book_set.add(name)
        return item

# Hard Code MySQL info.
# class MySQLPipelines(object):
#
#     dbconfig = {'host': '127.0.0.1',
#                 'user': 'root',
#                 'password': '123456',
#                 'database': 'crawl_book',
#                 'charset': 'utf8',
#                 'use_unicode': True}
#     table = 'book'
#
#     def __init__(self):
#         self.conn = None
#         self.cursor = None
#
#     def open_spider(self, spider):
#         self.conn = mysql.connector.connect(**self.dbconfig)
#         self.cursor = self.conn.cursor()
#
#     def close_spider(self, spider):
#         self.cursor.close()
#         self.conn.close()
#
#     def process_item(self, item, spider):
#         _SQL = """insert into book
#                   (name, price)
#                   values
#                   (%s, %s)"""
#         self.cursor.execute(_SQL, (item['name'],
#                                   item['price'],))
#         self.conn.commit()
#         return item

# Use settings.py.
class MySQLPipelines(object):

    @classmethod
    def from_crawler(cls, crawler):
        cls.dbconfig = crawler.settings.get('MYSQL_CONFIG', {})
        cls.table = crawler.settings.get('MYSQL_TABLE', '')
        return cls()

    def __init__(self):
        self.conn = None
        self.cursor = None

    def open_spider(self, spider):
        self.conn = mysql.connector.connect(**self.dbconfig)
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        _SQL = 'insert into ' + self.table +\
               ' (name, price) values (%s, %s)'
        self.cursor.execute(_SQL, (item['name'],
                                  item['price'],))
        self.conn.commit()
        return item
