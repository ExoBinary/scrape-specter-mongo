from pymongo import MongoClient
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve the MongoDB connection string from environment variables
MONGODB_URL = os.getenv("MONGODB_URL")

# Check if the MongoDB URL is set
if MONGODB_URL is None:
    raise ValueError("MongoDB URL not found in environment variables")

# Create a MongoDB client
client = MongoClient(MONGODB_URL)

# Access the database
db = client['crawled_domains']

# Define the collection for crawled domains
crawled_domains_collection = db['crawled_domains']

# Define the collection for crawled pages
crawled_pages_collection = db['crawled_pages']

def insert_crawled_domain(domain: str):
    """
    Insert crawled domain into MongoDB.
    
    :param domain: Domain to be inserted.
    """
    # Ensure the MongoDB client is initialized
    if client is None:
        raise ValueError("MongoDB client is not initialized")

    collection = db["crawled_domains"]
    collection.insert_one({"domain_url": domain, "status": "PENDING"})

def insert_crawled_page(page_url: str, content: str, crawled_domain_id: str):
    """
    Insert crawled page into MongoDB.
    
    :param page_url: URL of the crawled page.
    :param content: Content of the crawled page.
    :param crawled_domain_id: ID of the crawled domain to which the page belongs.
    """
    # Ensure the MongoDB client is initialized
    if client is None:
        raise ValueError("MongoDB client is not initialized")

    collection = db["crawled_pages"]
    collection.insert_one({"page_url": page_url, "content": content, "crawled_domain_id": crawled_domain_id})

# Define the CrawledDomains class
class CrawledDomains:
    def __init__(self, domain_url, status):
        self.domain_url = domain_url
        self.status = status

# Define the CrawledPages class
class CrawledPages:
    def __init__(self, page_url, content, crawled_domain_id):
        self.page_url = page_url
        self.content = content
        self.crawled_domain_id = crawled_domain_id

# Function to get the MongoDB database
def get_db():
    return db    
