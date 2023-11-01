from scrapy import Field, Item


class Ad(Item):
    title = Field()
    price = Field()
    condition = Field()
    date_sold = Field()
    itemID = Field()
