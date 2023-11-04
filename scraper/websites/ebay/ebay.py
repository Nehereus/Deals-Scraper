import urllib.parse
import re
import math
import scrapy
import os
from Ad import Ad
from utils import print_info, print_scraper
from scrapy.http import HtmlResponse


class Ebay(scrapy.Spider):
    name = 'ebay'

    def __init__(self, keyword, config, **kwargs):
        self.keyword = keyword
        self.config = config
        self.max_page = 1  # Default to one page, will be updated if FETCH_ALL is set
        super().__init__(**kwargs)

    def start_requests(self):
        """ Generate the initial request to get the number of pages if necessary. """
        print_scraper("EBAY", "Starting...")
        # Only get the number of pages if FETCH_ALL is set to 'true'
        url = self.build_search_url(self.keyword, self.config, 1)
        if os.getenv('FETCH_ALL', "False") == "True":
            yield scrapy.Request(url, callback=self.parse_initial)
        else:
            # Otherwise, just scrape the first page
            yield scrapy.Request(url, callback=self.parse_page)

    def build_search_url(self, keyword, config, page_number):
        """ Build the eBay search URL based on the keyword, config and page number. """
        params = {
            '_nkw': keyword,
            '_sop': '13',  # Ended Recently
            'LH_BIN': '1',  # Buy it now
            '_udlo': config["MinPrice"],
            '_udhi': config["MaxPrice"],
            'LH_Sold': 1,
            'LH_Complete': 1,
            "_ipg": "240",
            "_pgn": page_number  # Page number
        }
        return f"https://www.ebay.com/sch/i.html?{urllib.parse.urlencode(params)}"

    def parse_initial(self, response):
        """ Parse the initial response to get the total number of pages if FETCH_ALL is set. """
        if os.getenv('FETCH_ALL',"False")=="True":
            total_ads = response.xpath(
                '//*[@id="mainContent"]/div[1]/div/div[2]/div/div[1]/h1/span[1]/text()'
            ).extract_first()
            if total_ads:
                total_ads = int(total_ads.replace(",", ""))

                self.max_page = math.ceil(total_ads / 240)

        # Start scraping from the first page
        for page_number in range(1, self.max_page + 1):
            url = self.build_search_url(self.keyword, self.config, page_number)
            yield scrapy.Request(url, callback=self.parse_page)

    def parse_page(self, response):
        """ Parse each page to extract ads. """
        exclusion_keywords = ["laptop"]

        print_scraper("EBAY", "Scraping page...")
        all_ads = []

        if not response.xpath('//*[@id="srp-river-results"]/ul/li'):
            print_scraper("EBAY", "No results found")
            return

        print_scraper("EBAY", "Ads found")
        for ad in response.xpath('//li[@class="s-item s-item__pl-on-bottom"]'):
            title = ad.xpath('.//div[@class="s-item__title"]/span/text()').extract_first()
            price = ad.xpath('.//span[@class="s-item__price"]/span/text()').extract_first()
            date_sold = ad.xpath('.//span/text()').extract_first()
            condition = ad.xpath('.//span[@class="SECONDARY_INFO"]/text()').extract_first()
            item_url = ad.xpath('.//a[@class="s-item__link"]/@href').extract_first()

            if (not title
                    or not price
                    or "Shop on eBay" in title
                    or any(exclusion in title for exclusion in exclusion_keywords)):
                continue

            ad_item = Ad()
            ad_item["title"] = title
            ad_item["price"] = float(price.replace("$", "").replace(",", ""))
            ad_item["date_sold"] = ' '.join(date_sold.split()[1:])
            ad_item["condition"] = condition
            ad_item["itemID"] = re.search(r'/itm/(\d+)', item_url).group(1)
            all_ads.append(ad_item)

        return all_ads
