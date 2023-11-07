import time
import json
import os
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess
import set_min_max_price
from utils import print_info
from websites.ebay.ebay import Ebay


def main():
    shared_path = os.environ.get('SHARED_PATH')
    print_info("Activating Scraper...")
    interval = 24

    while True:
        # set the min/max price of the config.json before another round
        set_min_max_price.main()
        with open(f'{shared_path}/config.json', 'r') as f:
            config = json.load(f)

        for keyword, keyword_config in config.items():
            print_info(f"Scraping for keyword: {keyword}")
            p = Process(target=create_process, args=(Ebay, keyword, keyword_config))
            p.start()
            p.join()
            time.sleep(5)
        if os.getenv('FETCH_ALL', False):
            os.environ['FETCH_ALL'] = "False"
        time.sleep(60 * 60 * interval)


def create_process(classToCall, keyword, keyword_config):
    process = CrawlerProcess(settings={
        "USER_AGENT": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        "LOG_ENABLED": True,
        "ITEM_PIPELINES": {'pipeline.SQLitePipeline': 1},
        "SQLITE_TABLE_NAME": keyword
    })

    process.crawl(classToCall, keyword, keyword_config)
    process.start()
    return process


if __name__ == "__main__":
    print_info("Starting scraper")
    main()
