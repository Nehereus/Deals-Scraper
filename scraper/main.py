import time
import json
import os
from multiprocessing import Process
from scrapy.crawler import CrawlerProcess

from utils import print_info
from websites.ebay.ebay import Ebay


def main(config):
    print_info("Activating Scraper...")
    interval = 12

    while True:
        for keyword, keyword_config in config.items():
            print_info(f"Scraping for keyword: {keyword}")
            p = Process(target=create_process, args=(Ebay,keyword, keyword_config))
            p.start()
            p.join()
            time.sleep(5)
        time.sleep(60 * 60 * interval)


def create_process(classToCall, keyword, keyword_config):
    process = CrawlerProcess(settings={
        "USER_AGENT": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
        "LOG_ENABLED": True,
        "ITEM_PIPELINES": {'pipeline.SQLitePipeline': 1},
        "SQLITE_TABLE_NAME":keyword
    })

    process.crawl(classToCall,keyword, keyword_config)
    process.start()
    return process


if __name__ == "__main__":
    print_info("Starting scraper")
    shared_path= os.environ.get('SHARED_PATH')
    with open(f'{shared_path}/config.json', 'r') as f:
        config = json.load(f)
    main(config)
