"""Crawler for https://www.harpie.com.br"""
# import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class HarpieCrawler(CrawlSpider):
    name = "harpie_crawler"
    allowed_domains = ["www.harpie.com.br"]
    start_urls = ["https://www.harpie.com.br/"]

    rules = (
        # Rule(LinkExtractor(allow=r"catalogue/category")),
        # Rule(LinkExtractor(allow=r'index\.html$', deny=r'/books/'), callback='parse_item', follow=True)
    )

    def parse_item(self, response):
        item = {}
        return item
