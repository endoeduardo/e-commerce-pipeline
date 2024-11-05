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
            parse: Extracts all navigation links and follows them to parse individual items.
            parse_page: Extract links for further product detail.
            parse_item: Extract product information.

        Attributes:
            name (str): Name of the crawler.
            allowed_domains (list): Domains the crawler is allowed to access.
    """
    def __init__(self, *a, **kw):
        self.domain = "www.harpie.com.br"
        super().__init__(*a, **kw)

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
        yield from response.follow_all(links, self.parse_page)

    def parse_page(self, response: Response) -> Generator[dict, None, None]:
        """Parses each product listing page to extract product details.

        Args:
            response (Response): The response object containing product listing HTML content.

        Yields:
            product detailed page link
        """
        products = response.xpath(".//div[@id='lista-produtos-area']//li")
        for product in products:
            product_link = product.xpath(".//a/@href").get()
            if product_link:
                yield response.follow(product_link, callback=self.parse_item)
            else:
                pass

        next_page = response.xpath(".//li[@class='nav']/a/@href").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_page)
    
    def parse_item(self, response):
        product_page = response

        sizes = product_page.xpath(".//span[contains(text(), 'Tamanho')]/following-sibling::div[1]//div[@class='variacao-label']/text()").getall()
        available = product_page.xpath(".//span[contains(text(), 'Tamanho')]/following-sibling::div[1]//li/@data-estoque").getall()
        
        yield {
            "product_name": product_page.xpath(".//h1/text()").get(),
            "product_description": product_page.xpath(".//div[@class='product-description']/text()").get(),
            "SKU": product_page.xpath(".//span[@class='codigo-prod']/text()").get(),
            "one_time_payment": product_page.xpath(".//div[@class='full-price']//span[@class='price-big']/text()").get(),
            "quantity_of_payments": product_page.xpath(".//div[@class='type-payment']/strong/text()").get(),
            "payments_value": product_page.xpath(".//div[@class='type-payment']/span/strong/text()").get(),
            "color": product_page.xpath(".//div[@class='variacao-img-principal']/following-sibling::div[@class='variacao-label']/text()").get(),
            "variation": [{"size": size, "in_strock": product_available} for size, product_available in zip(sizes, available)],
            "rating": product_page.xpath(".//div[@class='rating-area']//strong/text()").get(),
            "number_of_ratings": product_page.xpath( ".//div[@class='rating-area']//p/text()").getall()
        }