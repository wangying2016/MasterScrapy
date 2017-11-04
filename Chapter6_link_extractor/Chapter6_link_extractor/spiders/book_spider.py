# -*-coding:utf-8-*-
from scrapy import Spider
from ..items import BookItem
from scrapy import Request
from scrapy.linkextractor import LinkExtractor
from scrapy import log

class BooksSpider(Spider):
    # 每一个爬虫的唯一标识
    name = 'books'

    # 定义爬虫爬取的起始点，起始点可以是多个，这里只有一个
    # start_urls = [
    #     'http://books.toscrape.com/'
    # ]

    # 实现 start_requests 方法，替代 start_urls 类属性
    def start_requests(self):
        yield Request('http://books.toscrape.com',
                      callback=self.parse,
                      headers={'User-Agent': 'Mozilla/5.0'},
                      dont_filter=True)

    def parse(self, response):
        # 提取数据
        # 每一本书的信息在 <article class="product_pod">中，我们使用
        # css() 方法找到所有这样的 article 元素，并依次迭代
        for sel in response.css('article.product_pod'):
            book = BookItem()
            # 书名信息在 article > h3 > a 元素的 title 属性里
            book['name'] = sel.xpath('./h3/a/@title').extract_first()
            # 例如：<a title="A light in the Attie">A Light in the...</a>
            # 书价信息在<p class="price_color"> 的 TEXT 中。
            book['price'] = sel.css('p.price_color::text').extract_first()
            yield book

        # 提取链接
        # 下一页的 url 在 ul.pager > li.next > a 里面
        le = LinkExtractor(restrict_css='ul.pager li.next')
        links = le.extract_links(response)
        if links:
            next_url = links[0].url
            self.logger.info('LinkExtractor: url = %s' % next_url)
            yield Request(next_url, callback=self.parse)

