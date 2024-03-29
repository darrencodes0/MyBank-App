from pymongo import MongoClient

#Input connection string into URL (replace with ur own MongoDB connection URL)
URL = "mongodb://localhost:27017"

client = MongoClient(URL)
db = client["users"]
user_collection = db["user_info"]
transactions_db = client["bank_transactions"]
transactions_collection = transactions_db["transactions"]