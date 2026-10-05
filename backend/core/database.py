import os 
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["agentic_platform"] 

customers_collection = db["customers"]
orders_collection = db["orders"] 

users_collection = db["users"]
audit_logs_collection = db["audit_logs"]
