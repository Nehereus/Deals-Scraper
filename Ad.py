from scrapy import Field, Item


class Ad(Item):
    title = Field()
    price = Field()
    description = Field()
    condition = Field()
    date_sold = Field()
    link = Field()
