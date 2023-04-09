# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import mysql.connector

class SavingToMySQLPipeline(object):

    def __init__(self):
        self.create_connection()

    def create_connection(self):
        self.conn = mysql.connector.connect(
            host = 'localhost',
            user = 'eitan',
            password = '123456',
            database = 'chocolate_scraping'
        )
        self.curr = self.conn.cursor()
    
    
    def process_item(self, item, spider):
        self.store_db(item)
        #we need to return the item below as Scrapy expects us to!
        return item

    
    def store_db(self, item):
        self.curr.execute("insert into chocolate_products ( name, price, url)  values (%s,%s,%s)", (
            item["name"],
            item["price"],
            item["url"]
        ))
        self.conn.commit()


class PriceToUSDPipeline:

    gbpToUsdRate = 1.3

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # check is price present
        if adapter.get('price'):

            # converting the price to a float
            floatPrice = float(adapter['price'])

            # converting the price from gbp to usd using our hard coded exchange rate
            adapter['price'] = floatPrice * self.gbpToUsdRate

            return item

        else:
            # drop item if no price
            raise DropItem(f"Missing price in {item}")




class DuplicatesPipeline:

    def __init__(self):
        self.names_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['name'] in self.names_seen:
            raise DropItem(f"Duplicate item found: {item!r}")
        else:
            self.names_seen.add(adapter['name'])
            return item
