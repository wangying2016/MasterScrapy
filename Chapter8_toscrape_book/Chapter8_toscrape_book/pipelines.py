# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import mysql.connector

class BookPipeline(object):
    review_rating_map = {
        'One': 1,
        'Two': 2,
        'Three': 3,
        'Four': 4,
        'Five': 5,
    }

    def process_item(self, item, spider):
        rating = item.get('review_rating')
        if rating:
            item['review_rating'] = self.review_rating_map[rating]
        return item


class MySQLPipeline:

    def open_spider(self, spider):
        db = spider.settings.get('MYSQL_DB_NAME', 'crawl_book')
        host = spider.settings.get('MYSQL_HOST', 'localhost')
        port = spider.settings.get('MYSQL_PORT', '3306')
        user = spider.settings.get('MYSQL_USER', 'root')
        passwd = spider.settings.get('MYSQL_PASSWORD', '123456')

        self.dbconfig = {
            'host': host,
            'user': user,
            'port': port,
            'password': passwd,
            'database': db
        }

        self.conn = mysql.connector.connect(**self.dbconfig)
        self.cursor = self.conn.cursor()

    def close_spider(self, spider):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def process_item(self, item, spider):
        self.insert_db(item)
        return item

    def insert_db(self, item):
        values = (
            item['upc'],
            item['name'],
            item['price'],
            item['review_rating'],
            item['review_num'],
            item['stock'],
        )

        sql = 'insert into book values(%s, %s, %s, %s, %s, %s)'
        self.cursor.execute(sql, values)

