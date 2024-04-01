import scrapy
import re
from urllib.parse import urlparse
from pymongo import MongoClient
import os
from dotenv import load_dotenv

class PyppeteerSpider(scrapy.Spider):
    name = 'pyppeteer_spider'
    page_count = 0
    max_pages = 10

    load_dotenv()


    def __init__(self, *args, **kwargs):
        MONGODB_URL = os.getenv("MONGODB_URL")
        if MONGODB_URL is None:
           raise ValueError("MongoDB URL not found in environment variables")
        super().__init__(*args, **kwargs)
        self.domain_id = None
        self.mongo_client = MongoClient(MONGODB_URL)
        self.db = self.mongo_client['crawled_domains']

    def spider_closed(self, spider, reason):
        status = 'COMPLETED' if reason == 'finished' else 'FAILURE'
        if self.domain_id:
            domain = self.db['crawled_domains'].find_one({"_id": self.domain_id})
            if domain:
                domain['status'] = status
                self.db['crawled_domains'].update_one({"_id": self.domain_id}, {"$set": domain})
                print("Domain status updated:", domain)

    def start_requests(self):
        for url in self.start_urls:
            domain_url = urlparse(url).netloc
            domain = {"domain_url": domain_url, "status": "PENDING"}
            self.domain_id = self.db['crawled_domains'].insert_one(domain).inserted_id
            print("Inserted domain with ID:", self.domain_id)
            yield scrapy.Request(url, meta={'pyppeteer': True, 'domain_id': str(self.domain_id)})
       

    def parse(self, response):
        
        if self.page_count < self.max_pages:
            self.page_count += 1
            visible_texts = response.xpath('//body//*[not(self::script or self::style or self::meta or self::link)]/text()').getall()

            clean_text = ' '.join([re.sub(r'\s+', ' ', node).strip() for node in visible_texts if node.strip()])
            page = self.db['scrapped_pages'].find_one({"page_url": response.url})           


            if page:
                page["content"] = clean_text
                self.db['scrapped_pages'].update_one({"_id": page["_id"]}, {"$set": page})
                print("Page updated in database:", page)
            else:
                page_data = { "page_url": response.url, "page_size": len(response.body), "page_content": clean_text, "crawled_domain_id": response.meta['domain_id']}
                self.db['scrapped_pages'].insert_one(page_data)
                print("Page inserted into database:", page_data)

            current_domain = urlparse(response.url).netloc
            # self.mongo_client.close()
            # print("MongoDB client closed.")
            for a in response.css('a::attr(href)'):
                link = a.extract()
                link_domain = urlparse(link).netloc
                if current_domain == link_domain or not link_domain:
                    yield response.follow(a, self.parse, meta={'domain_id': response.meta['domain_id']})
