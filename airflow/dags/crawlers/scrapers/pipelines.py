"""Define your item pipelines here

Don't forget to add your pipeline to the ITEM_PIPELINES setting
See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


useful for handling different item types with a single interface
"""
# pylint: skip-file: W0613

from typing import Any
import re
import logging
import pymongo
from itemadapter import ItemAdapter
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured

class ECommercePipeline:
    """
    A pipeline that processes items by cleaning specific fields, 
    formatting SKU, price, and quantity fields for standardized storage.
    """
    collection_name: str = "ECommerceCollection"

    def __init__(self, mongo_uri: str, mongo_db: str) -> None:
        """
        Initializes the pipeline with the MongoDB URI and database name.
        
        Args:
            mongo_uri (str): URI for MongoDB connection.
            mongo_db (str): Name of the MongoDB database.
        """
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.client = None  # This will hold the MongoDB client connection
        self.db = None

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> 'ECommercePipeline':
        """
        Factory method that initializes the pipeline from Scrapy crawler settings.
        
        Args:
            crawler (Crawler): The Scrapy crawler instance containing settings.
        
        Returns:
            ECommercePipeline: An instance of the ECommercePipeline with settings applied.
        """
        if not crawler.settings.getbool('E_COMMERCE_PIPELINE'):
            # if this isn't specified in settings, the pipeline will be completely disabled
            raise NotConfigured
        return cls(
            mongo_uri=crawler.settings.get("MONGO_URI"),
            mongo_db=crawler.settings.get("MONGO_DATABASE", "items"),
        )

    def open_spider(self, spider) -> None:
        """
        Opens the MongoDB connection when the spider is opened.
        
        Args:
            spider: The Scrapy spider instance that is opened.
        """
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider) -> None:
        """
        Closes the MongoDB connection when the spider is closed.
        
        Args:
            spider: The Scrapy spider instance that is closed.
        """
        if self.client:
            self.client.close()

    def process_item(self, item: Any, spider: Any) -> Any: # pylint: disable=unused-argument
        """
        Process an item scraped by the spider.

        This method cleans unnecessary characters from the SKU field,
        converts price fields to floats, and transforms the quantity of
        payments into an integer. Fields are pre-cleaned to remove
        extraneous whitespace or newline characters.

        Args:
            item: The item scraped by the spider.
            spider: The spider instance that scraped the item.

        Returns:
            The cleaned item with formatted fields.
        """
        adapter = ItemAdapter(item)

        self.clean_fields(adapter)

        # Clean SKU field
        sku = adapter.get("SKU")
        if sku:
            adapter["SKU"] = sku.replace("SKU: ", "")

        # Convert price fields to float
        for field in ["one_time_payment", "payments_value"]:
            price = adapter.get(field)
            if price:
                adapter[field] = self._parse_price(price)

        # Convert quantity of payments to integer
        quantity = adapter.get("quantity_of_payments")
        if quantity:
            adapter["quantity_of_payments"] = self._parse_quantity(quantity)

        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item

    def clean_fields(self, adapter: ItemAdapter) -> None:
        """
        Clean unnecessary characters from all fields except excluded ones.

        Args:
            adapter: The item adapter wrapping the item for field access.
        """
        excluded_fields = {"in_stock", "rating", "number_of_ratings", "variation"}

        for field in adapter.field_names():
            if field not in excluded_fields:
                value = adapter.get(field)
                if value is not None:
                    adapter[field] = self.clean_value(value)

    def clean_value(self, value: Any) -> Any:
        """
        Strip whitespace and newline characters from a value.

        Args:
            value: The value to clean.

        Returns:
            The cleaned value, or the original value if cleaning fails.
        """
        try:
            return value.strip().replace("\n", "")
        except AttributeError as error:
            logging.error("Error cleaning value: %s", error, exc_info=True)
            return value

    def _parse_price(self, price: str) -> float:
        """
        Parse a price string by removing currency symbols and commas,
        then convert to float.

        Args:
            price: The price string to parse.

        Returns:
            The parsed price as a float.
        """
        return float(price.replace(",", ".").replace("R$", ""))

    def _parse_quantity(self, quantity: str) -> int:
        """
        Parse a quantity string by removing non-numeric characters.

        Args:
            quantity: The quantity string to parse.

        Returns:
            The parsed quantity as an integer.
        """
        return int(quantity.replace("x", ""))
    
    def _parse_number_of_ratings(self, number_of_ratings: str) -> int:
        """
        Parse a quantinty string by removing non-numeric characters.

        Args:
            number_of_ratings: The quantings strings to clean.
        
        Returns:
            The parsed quantity as an integer.
        """
        try:
            number_of_ratings = re.findall(r"\d", number_of_ratings)
            number_of_ratings = "".join(number_of_ratings)
            number_of_ratings = int(number_of_ratings)
            return number_of_ratings
        
        except TypeError as error:
            logging.info(f"Invalid number of ratings type, Error: {error}")
            return None
