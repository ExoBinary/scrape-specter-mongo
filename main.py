from fastapi import FastAPI, HTTPException
from multiprocessing import Manager, Process, freeze_support
from urllib.parse import urlparse
import re
import uvicorn
from modules.spider import PyppeteerSpider
from modules.database import insert_crawled_domain
from pymongo import MongoClient
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from dotenv import load_dotenv
import os


# Initialize FastAPI application
app = FastAPI()
load_dotenv()

# Retrieve the MongoDB connection string from environment variables
MONGODB_URL = os.getenv("MONGODB_URL")

# Check if the MongoDB URL is set
if MONGODB_URL is None:
    raise ValueError("MongoDB URL not found in environment variables")


# Declare global variables for manager and lock dictionary
manager = None
lock_dict = None
mongo_client = None

def run_crawler(domain):
    """
    Run the Scrapy crawler for the given domain.
    """
    try:
        # Create a Scrapy crawler process
        process = CrawlerProcess(settings=get_project_settings())

        # Run the spider for the given domain
        process.crawl(PyppeteerSpider, start_urls=[domain])
        # Start the crawling process
        process.start()
    except Exception as e:
        # In case of any exception, raise HTTP 500 error
        raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")


@app.post("/crawl/")
async def crawl(url: str):
    """
    API endpoint to initiate web crawling.

    :param url: URL to crawl.
    :return: Response indicating the crawling initiation status.
    """
    global lock_dict, mongo_client

    # Ensure URL starts with http or https
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url

    # Validate URL format
    if not re.match(r'(http|https)://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', url):
        raise HTTPException(status_code=400, detail="Invalid URL format")

    # Extract domain from URL
    parsed_url = urlparse(url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

    # Check and set lock for the domain
    if lock_dict is None:
        manager = Manager()
        lock_dict = manager.dict()
    if domain in lock_dict and lock_dict[domain]:
        return {"detail": f"Crawling initiated for domain: {domain}"}
    lock_dict[domain] = True

    # Insert domain into MongoDB
    insert_crawled_domain(domain)

    # Initiate crawling in a separate process
    p = Process(target=run_crawler, args=(domain,))
    p.start()

    return {"detail": f"Crawling initiated for domain: {domain}"}

if __name__ == "__main__":
    # Ensure proper multiprocessing support on Windows
    freeze_support()

    # Connect to MongoDB
    mongo_client = MongoClient(MONGODB_URL)

    # Start the FastAPI application
    uvicorn.run(app, host="0.0.0.0", port=8039)
