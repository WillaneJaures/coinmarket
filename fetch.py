from pymongo import MongoClient
import pandas as pd


username = "user1"
password = "user1"
auth_db = "admin"

client = MongoClient(f"mongodb://{username}:{password}@localhost:27017/?authSource={auth_db}")

client.admin.command('ping')
print("Successfully connected to MongoDB!")

db = client["coinmarketdata"]
collection = db["coinmarketdata"]

data = list(collection.find())
#convert to pandas dataframe
df = pd.DataFrame(data)

#df.to_csv('coinmarketdata.csv', index=False)