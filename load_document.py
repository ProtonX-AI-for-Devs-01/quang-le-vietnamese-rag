import pandas as pd
import json
from rag.mongo_client import MongoClient
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

crawled_dataset_df = pd.read_json('output.json')
print(crawled_dataset_df.head(5))

embedding_model = SentenceTransformer("keepitreal/vietnamese-sbert")

def get_embedding(text: str) -> list[float]:
    if not text.strip():
        print("Attempted to get embedding for empty text.")
        return []

    embedding = embedding_model.encode(text)

    return embedding.tolist()

crawled_dataset_df["embedding"] = crawled_dataset_df["content"].apply(get_embedding)

crawled_dataset_df.head()

load_dotenv()  # Load environment variables from .env file
mongo_uri = os.getenv('MONGO_URI')
db_name = os.getenv('DB_NAME')
db_collection = os.getenv('DB_COLLECTION')

mongo_client = MongoClient().get_mongo_client(mongo_uri)

db = mongo_client[db_name]
collection = db[db_collection]
documents = crawled_dataset_df.to_dict("records")
collection.insert_many(documents)

print("Data ingestion into MongoDB completed")