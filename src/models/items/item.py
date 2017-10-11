import uuid
from bs4 import BeautifulSoup
import requests
import re
from src.common.database import Database
import src.models.items.constants as ItemConstants
from src.models.stores.store import Store

__author__ = 'jslvtr'


class Item(object):
    def __init__(self, name, url, price=None, _id=None):
        self.name = name
        self.url = url
        store = Store.find_by_url(url)
        self.tag_name = store.tag_name
        self.query = store.query
        self.price = None if price is None else price
        self._id = uuid.uuid4().hex if _id is None else _id

    def __repr__(self):
        return "<Item {} with URL {}>".format(self.name, self.url)

    def load_price(self):
        # Amazon: <span id="priceblock_ourprice" class="a-size-medium a-color-price">$2,499.00</span>
        request = requests.get(self.url)
        content = request.content
        soup = BeautifulSoup(content, "html.parser")
        element = soup.find(self.tag_name, self.query)
        string_price = element.text.strip()
        string_price = string_price.replace(' ','')   # french has spaces as thousands separators, so eliminate spaces
        pattern = re.compile("((?:(?:\d+)*[\.|\,])*\d+)")  # Select only digits and "," or "." (delete currency symbols)
        string_price = pattern.search(string_price).group()
        eu_pattern = re.compile("\d*\.\d*\,")
        us_pattern = re.compile("\d*\,\d*\.")
        if eu_pattern.search(string_price):         # if thousand separator = '.' and decimal sep. = ","
            string_price.replace('.','')            # then delete '.' and afterwards change ',' into '.'
            string_price.replace(',','.')
        elif us_pattern.search(string_price):       # if thousand separator = ','
            string_price.replace(',','')            # then delete all ','
        string_price = string_price.replace(',','.')    # if number only contains one ',' then change it to '.'
        try:
            self.price = float(string_price)
        except ItemErrors.StringToFloatError as e:
            return e.message

        return self.price

    def save_to_mongo(self):
        Database.update(ItemConstants.COLLECTION, {'_id': self._id}, self.json())

    def json(self):
        return {
            "_id": self._id,
            "name": self.name,
            "url": self.url,
            "price": self.price
        }

    @classmethod
    def get_by_id(cls, item_id):
        return cls(**Database.find_one(ItemConstants.COLLECTION, {"_id": item_id}))
