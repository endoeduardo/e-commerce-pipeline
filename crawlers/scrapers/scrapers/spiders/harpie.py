"""Crawler for https://www.harpie.com.br using Scrapy framework."""
from typing import Generator

import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.http import Response

class HarpieCrawler(CrawlSpider):
    """This crawler extracts product information such as product name, price (via PIX),
        small price, and installment quantity from the e-commerce site https://www.harpie.com.br.

        Classes:
            HarpieCrawler: Inherits from CrawlSpider to crawl the product listings.

        Methods:
            start_requests: Initiates crawling at the homepage.
            parse_page: Extracts all navigation links and follows them to parse individual items.
            parse_item: Extracts specific product details from a given page.

        Attributes:
            name (str): Name of the crawler.
            allowed_domains (list): Domains the crawler is allowed to access.
    """
    name = "harpie_crawler"
    allowed_domains = ["www.harpie.com.br"]

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """Initiates the crawl by sending a request to the homepage.

        Yields:
            scrapy.Request: Request object pointing to the homepage URL.
        """
        starting_url = "https://www.harpie.com.br/"
        yield scrapy.Request(starting_url, self.parse)

    def parse(self, response: Response) -> Generator[scrapy.Request, None, None]: # pylint: disable=arguments-differ
        """Parses the homepage to extract navigation links to product listings.

        Args:
            response (Response): The response object containing the homepage HTML content.

        Yields:
            scrapy.Request: Requests for following product listing links.
        """
        links = response.xpath(".//ul[@id='nav-root']//a/@href").getall()
        yield from response.follow_all(links, self.parse_item)

    def parse_item(self, response: Response) -> Generator[dict, None, None]:
        """Parses each product listing page to extract product details.

        Args:
            response (Response): The response object containing product listing HTML content.

        Yields:
            dict: A dictionary with product details, including 'product_name', 'pix', 'preco',
                  and 'qte_parcelamento'.
        """
        products = response.xpath(".//div[@id='lista-produtos-area']//li")
        for product in products:
            yield {
                "product_name": product.xpath(".//h3/text()").get(),
                "pix": product.xpath(".//span[@class='pix']/text()").get(),
                "preco": product.xpath(".//span[@class='small-price']/text()").get(),
                "qte_parcelamento": product.xpath(".//div[@class='secondary-price flex wrap center justify-center']/text()").get()  # pylint: disable=line-too-long
            }
