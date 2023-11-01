import sqlite3
import os
from scrapy.exceptions import DropItem
from datetime import datetime

class SQLitePipeline:
    def __init__(self, table_name):
        self.table_name = table_name
        self.database_path = os.environ.get('SHARED_PATH')+"/items_database.db"

    @classmethod
    def from_crawler(cls, crawler):
        table_name = crawler.settings.get('SQLITE_TABLE_NAME', 'default_table')
        return cls(table_name)

    def open_spider(self, spider):
        self.conn = sqlite3.connect(self.database_path)
        self.c = self.conn.cursor()

        self.c.execute(f'''
            CREATE TABLE IF NOT EXISTS "{self.table_name}" (
                id INTEGER PRIMARY KEY,
                title TEXT,
                price REAL,
                condition TEXT,
                date_sold TEXT,
                itemID TEXT UNIQUE
            )
        ''')
        self.conn.commit()

    def close_spider(self, spider):
        self.conn.close()


    def process_item(self, item, spider):
        def convert_date(date_str):
            return datetime.strptime(date_str, '%b %d, %Y').strftime('%Y-%m-%d')

        # Check if itemID exists in the database
        self.c.execute(f'SELECT itemID FROM "{self.table_name}" WHERE itemID = ?', (item['itemID'],))
        result = self.c.fetchone()
        if result:
            # If itemID exists, raise a DropItem exception
            raise DropItem(f"Duplicate item found: {item['itemID']}")
        else:
            # Otherwise, insert the new item
            date_sold = convert_date(item['date_sold'])
            self.c.execute(f'''
            INSERT INTO "{self.table_name}" (title, price, condition, date_sold, itemID)
            VALUES (?, ?, ?, ?, ?)
            ''', (item['title'], item['price'], item['condition'], date_sold, item['itemID']))
            self.conn.commit()

        return item


