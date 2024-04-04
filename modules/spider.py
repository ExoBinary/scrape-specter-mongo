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
    visited_domains = set()  # Maintain a set of visited domains

    load_dotenv()


    def __init__(self, *args, **kwargs):
        MONGODB_URL = os.getenv("MONGODB_URL")
        if MONGODB_URL is None:
           raise ValueError("MongoDB URL not found in environment variables")
        super().__init__(*args, **kwargs)
        self.domain_id = None
        self.mongo_client = MongoClient(MONGODB_URL)
        self.db = self.mongo_client['crawled_domains']

      

    def parse(self, response):
        if self.page_count < self.max_pages:
            self.page_count += 1
            visible_texts = response.xpath('//body//*[not(self::script or self::style or self::meta or self::link)]/text()').getall()
            print("Response body:", response.body)

            clean_text = ' '.join([re.sub(r'\s+', ' ', node).strip() for node in visible_texts if node.strip()])

            # Extract main domain from the response URL
            main_domain = urlparse(response.url).netloc

            # Check if the page URL is valid
            if response.url.startswith("http"):
                # Check if content is not empty
                if clean_text:
                    # Page data
                    page_data = {
                        "page_url": response.url,
                        "page_content": clean_text,
                        "page_size": len(response.body)
                    }

                    # Check if the domain is currently being processed
                    domain_document = self.db['scrapped_pages'].find_one({"domain": main_domain, "status": "processing"})

                    if domain_document:
                        # Domain is currently being processed, update existing document
                        self.db['scrapped_pages'].update_one(
                            {"_id": domain_document["_id"]},
                            {"$push": {"pages": page_data}}
                        )
                        print("Page inserted into existing domain document:", page_data)
                    else:
                        # Domain is not currently being processed, insert new document
                        domain_data = {
                            "domain": main_domain,
                            "pages": [page_data],
                            "status": "processing"  # Set status to processing
                        }
                        self.db['scrapped_pages'].insert_one(domain_data)
                        print("New domain document created with page:", page_data)
                else:
                    print("Skipping empty page:", response.url)

            current_domain = urlparse(response.url).netloc
            for a in response.css('a::attr(href)'):
                link = a.extract()
                link_domain = urlparse(link).netloc
                if current_domain == link_domain or not link_domain:
                    yield response.follow(a, self.parse, meta={'domain_id': main_domain})

        # Check if all pages are processed and update status to done
        if self.page_count >= self.max_pages:
            self.db['scrapped_pages'].update_many(
                {"domain": main_domain, "status": "processing"},
                {"$set": {"status": "done"}}
            )
            print("All pages processed for domain:", main_domain)
    