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

# Define the collection for crawled pages
crawled_pages_collection = db['crawled_pages']


# Function to get the MongoDB database
def get_db():
    return db    
