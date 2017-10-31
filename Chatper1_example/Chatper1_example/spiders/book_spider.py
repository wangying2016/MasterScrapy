# -*-coding:utf-8-*-
import scrapy


class BooksSpider(scrapy.Spider):
    # 每一个爬虫的唯一标识
    name = 'books'

    # 定义爬虫爬取的起始点，起始点可以是多个，这里只有一个
    # start_urls = [
    #     'http://books.toscrape.com/'
    # ]

    # 实现 start_requests 方法，替代 start_urls 类属性
    def start_requests(self):
        yield scrapy.Request('http://books.toscrape.com',
                             callback=self.parse,
                             headers={'User-Agent': 'Mozilla/5.0'},
                             dont_filter=True)

    def parse(self, response):
        # 提取数据
        # 每一本书的信息在 <article class="product_pod">中，我们使用
        # css() 方法找到所有这样的 article 元素，并依次迭代
        for book in response.css('article.product_pod'):
            # 书名信息在 article > h3 > a 元素的 title 属性里
            # 例如：<a title="A light in the Attie">A Light in the...</a>
            name = book.xpath('./h3/a/@title').extract_first()

            # 书价信息在<p class="price_color"> 的 TEXT 中。
            price = book.css('p.price_color::text').extract_first()

            yield {
                'name': name,
                'price': price,
            }

        # 提取链接
        next_url = response.css('ul.pager li.next a::attr(href)').extract_first()
        if next_url:
            next_url = response.urljoin(next_url)
            yield scrapy.Request(next_url, callback=self.parse)