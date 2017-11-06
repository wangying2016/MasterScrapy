# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from ..items import BookItem


class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['http://books.toscrape.com/']

    # 书籍列表页面的解析函数
    def parse(self, response):
        # 提取书籍列表页面中每本书的链接
        le = LinkExtractor(restrict_css='article.product_pod')
        for link in le.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_book)

        # 提取“下一页”的链接
        le = LinkExtractor(restrict_css='ul.pager li.next')
        links = le.extract_links(response)
        if links:
            next_url = links[0].url
            yield scrapy.Request(next_url, callback=self.parse)

    # 书籍页面的解析函数
    def parse_book(self, response):
        book = BookItem()
        info = response.css('div.product_main')
        book['name'] = info.css('h1::text').extract_first()
        book['price'] = info.css('p.price_color::text').extract_first()
        book['review_rating'] = info.css('p.star-rating::attr(class)'
                                         ).re_first('star-rating\s([A-Za-z]+)$')
        table = response.css('table.table-striped')
        book['upc'] = table.xpath('.//tr[1]/td/text()').extract_first()
        book['stock'] = table.xpath('.//tr[last() - 1]/td/text()'
                                    ).re_first('\((\d+)\savailable\)')
        book['review_num'] = table.xpath('.//tr[last()]/td/text()'
                                         ).extract_first()
        yield book

