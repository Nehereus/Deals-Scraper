import urllib.parse
import re
import scrapy

from Ad import Ad
from utils import print_info, print_scraper


class Ebay(scrapy.Spider):
    name = 'ebay'

    def __init__(self, keyword,config, **kwargs):
        print_scraper("EBAY", "Starting...")
        # build the URL
        min_price = config["MinPrice"]
        max_price = config["MaxPrice"]
        url = f"https://www.ebay.com/sch/i.html?"
        url += urllib.parse.urlencode(
            # LH_BIN = buy it now, _sop 13 = Ended Recently
            # crawl completed and sold item only
            {'_nkw': keyword, '_sop': '13', 'LH_BIN': '1', '_udlo': min_price, '_udhi': max_price,
             'LH_Sold': 1, 'LH_Complete': 1, "_ipg": 240})
        self.start_urls = [url]  # set the url to the spider
        super().__init__(**kwargs)

    def parse(self, response):
        exclusion_keywords=["laptop"]

        print_scraper("EBAY", "Scraping...")
        allAds = []

        if (response.xpath('//*[@id="srp-river-results"]/ul/li') == None):
            print_scraper("EBAY", "No results found")
            return None
        print_scraper("EBAY", "Ads found")

        # each flex item box (each ad)
        for ads in response.xpath('//li[@class="s-item s-item__pl-on-bottom"]'):
            title = ads.xpath('.//div[@class="s-item__title"]/span/text()').extract_first()
            price = ads.xpath('.//span[@class="s-item__price"]/span/text()').extract_first()
            r_date_sold = ads.xpath('.//span/text()').extract_first()
            condition = ads.xpath('.//span[@class="SECONDARY_INFO"]/text()').extract_first()
            item_url = ads.xpath('.//a[@class="s-item__link"]/@href').extract_first()
            # ebay has "1$ to 2$" options and those are definetly not what we are looking for.
            if price == None:
                continue

            # ebay has ads who are usually unrelated to our specific search.
            if title == None or title == "Shop on eBay":
                continue
            if any(key in title for key in exclusion_keywords):
                continue

            date_sold = ' '.join(r_date_sold.split()[1:])

            ad = Ad()
            ad["title"] = title
            ad["price"] = float(price[1:].replace(",", ""))
            ad["date_sold"] = date_sold
            ad["condition"] = condition
            ad["itemID"] = re.search(r'/itm/(\d+)', item_url).group(1)
            allAds.append(ad)
        return allAds
