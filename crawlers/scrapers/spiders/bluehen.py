"""Crawler for https://www.bluhen.com.br/ using Scrapy framework."""
# pylint: skip-file: E0401
from typing import Generator, List, Dict, Union, Any
import scrapy
from scrapy.spiders import CrawlSpider
from scrapy.http import Response
from scrapers.items import ClothingItem
from datetime import datetime


class BluhenCrawler(CrawlSpider):
    """
    A Scrapy crawler that extracts product information from the e-commerce 
    site https://www.bluhen.com.br/, including product name, price,
    installment options, and availability details.

    Attributes:
        name (str): The name identifier for the crawler.
        allowed_domains (List[str]): Domains that the crawler is permitted to access.
        domain (str): The base domain of the target site.

    Methods:
        start_requests: Initiates the crawling process by sending a request to the homepage.
        parse: Parses the homepage to extract navigation links for product categories.
        parse_page: Parses product listing pages to retrieve links to individual product pages.
        parse_item: Extracts detailed product information from each product's page.
    """

    name: str = "bluhen_crawler"
    allowed_domains: List[str] = ["www.bluhen.com.br"]
    custom_settings = {
        "E_COMMERCE_PIPELINE": True
    }

    def __init__(self, *args, **kwargs):
        """
        Initializes the BluehenCrawler with specified arguments and sets the base domain.
        """
        self.domain: str = "www.bluhen.com.br"
        super().__init__(*args, **kwargs)

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """
        Initiates the crawl by sending a request to the homepage.

        Yields:
            Generator[scrapy.Request, None, None]: A request object for the homepage URL.
        """
        starting_url = "https://www.bluhen.com.br/"
        yield scrapy.Request(starting_url, self.parse)

    def parse(self, response: Response) -> Generator[scrapy.Request, None, None]:  # pylint: disable=arguments-differ
        """
        Parses the homepage to extract navigation links for product categories.

        Args:
            response (Response): The response object containing the homepage HTML content.

        Yields:
            Generator[scrapy.Request, None, None]: Requests for each product category link.
        """
        links: List[str] = response.xpath(".//ul[@id='nav-root']//a/@href").getall()
        links = [link.replace("//", "").replace("www.bluhen.com.br", "") for link in links]
        yield from response.follow_all(links, self.parse_page)

    def parse_page(
        self,
        response: Response
    ) -> Generator[Union[scrapy.Request, Dict[str, Union[str, List[Dict[str, Union[str, bool]]]]]], None, None]: # pylint: disable=line-too-long
        """
        Parses a product listing page to extract links for individual product details.

        Args:
            response (Response): 
                The response object containing the HTML content of a product listing page.

        Yields:
            Generator[Union[scrapy.Request, Dict[str, Union[str, List[Dict[str, Union[str, bool]]]]]], None, None]: # pylint: disable=line-too-long
            Requests to follow product detail links or extracted product information if available.
        """
        products = response.xpath(".//div[@id='lista-produtos-area']//li")
        for product in products:
            product_link = product.xpath(".//a/@href").get()
            if product_link:
                yield response.follow(product_link, callback=self.parse_item)

        next_page = response.xpath(".//li[@class='nav']/a/@href").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse_page)

# pylint: disable=line-too-long
    def parse_item(self, response: Response) -> Generator[Any, Any, Any]:
        """
        Extracts detailed product information from an individual product page.

        Args:
            response (Response): The response object containing the HTML content of a product page.

        Returns:
            Dict[str, Union[str, List[Dict[str, Union[str, bool]]]]]: 
                A dictionary containing product details.
        """
        item = ClothingItem()

        product_page = response

        sizes = product_page.xpath(".//span[contains(text(), 'Tamanho')]/following-sibling::div[1]//div[@class='variacao-label']/text()").getall() # pylint: disable=line-too-long
        available = product_page.xpath(".//span[contains(text(), 'Tamanho')]/following-sibling::div[1]//li/@data-estoque").getall() # pylint: disable=line-too-long
        item["product_name"] = product_page.xpath(".//h1/text()").get()
        item["product_link"] = response.request.url
        item["product_description"] = product_page.xpath(".//div[@class='content']/h2/text()").get()
        item["SKU"] = None
        item["one_time_payment"] = product_page.xpath(".//span[@class='price-big']/text()").get()
        item["quantity_of_payments"] = product_page.xpath(".//div[@class='type-payment']/strong/text()").get()
        item["payments_value"] = product_page.xpath(".//div[@class='full-price flex']/span[@class='price-big']/text()").get()
        item["color"] = product_page.xpath(".//div[@class='variacao-img-principal']/following-sibling::div[@class='variacao-label']/text()").get()
        item["variation"] = [{"size": size, "in_stock": stock == '1'} for size, stock in zip(sizes, available)]
        item["rating"] = product_page.xpath(".//a[@class='avaliacoes-link']/span/@data-value").get()
        item["number_of_ratings"] = product_page.xpath(".//span[@class='num-avaliacoes']/a/text()").get()
        item["timestamp"] = datetime.now().strftime(format="%Y-%m-%d %H:%M:%S")

        yield item
# pylint: enable=line-too-long
