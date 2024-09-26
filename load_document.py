import pandas as pd
import json
from rag.mongo_client import MongoClient
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

crawled_dataset_df = pd.read_json('output.json')
print(crawled_dataset_df.head(5))

from spacy.lang.vi import Vietnamese
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import math

# Load the spaCy model for sentence segmentation
nlp = Vietnamese()
nlp.add_pipe('sentencizer')

# Semantic splitting based on sentence boundaries and similarity
def semantic_splitting(text, threshold=0.2):
    # Parse the document
    doc = nlp(text)
    sentences = [sent.text for sent in doc.sents]  # Extract sentences

    # Vectorize the sentences for similarity checking
    vectorizer = TfidfVectorizer().fit_transform(sentences)
    vectors = vectorizer.toarray()

    # Calculate pairwise cosine similarity between sentences
    similarities = cosine_similarity(vectors)

    # Initialize chunks with the first sentence
    chunks = [[sentences[0]]]

    # Group sentences into chunks based on similarity threshold
    for i in range(1, len(sentences)):
        sim_score = similarities[i-1, i]

        if sim_score >= threshold:
            # If the similarity is above the threshold, add to the current chunk
            chunks[-1].append(sentences[i])
        else:
            # Start a new chunk
            chunks.append([sentences[i]])

    # Join the sentences in each chunk to form coherent paragraphs
    return [' '.join(chunk) for chunk in chunks]

# Example usage

dataset_df = pd.DataFrame()
# Perform semantic splitting
for index, row in crawled_dataset_df.iterrows():
    if len(row['content']) > 0:
        semantic_chunks = semantic_splitting(row['content'])

        # Print the chunks
        for idx, chunk in enumerate(semantic_chunks):
            print(f"Chunk {idx+1}:\n{chunk}\n")
            dataset_df = dataset_df.append({
                "url":  row['url'],
                "price":  row['price'],
                "title": row['title'],
                "image_urls": row['image_urls'],
                'content': chunk,
            }, ignore_index=True)

print(dataset_df.head(5))
# drop rows with empty content
dataset_df['content'].replace('', math.nan, inplace=True)
dataset_df.dropna(subset=['content'], inplace=True)

embedding_model = SentenceTransformer("keepitreal/vietnamese-sbert")

def get_embedding(text: str) -> list[float]:
    if not text.strip():
        print("Attempted to get embedding for empty text.")
        return []

    embedding = embedding_model.encode(text)

    return embedding.tolist()

dataset_df["embedding"] = dataset_df["content"].apply(get_embedding)

dataset_df.head()

load_dotenv()  # Load environment variables from .env file
mongo_uri = os.getenv('MONGO_URI')
db_name = os.getenv('DB_NAME')
db_collection = os.getenv('DB_COLLECTION')

mongo_client = MongoClient().get_mongo_client(mongo_uri)

db = mongo_client[db_name]
collection = db[db_collection]
# clear collection
collection.delete_many({})
documents = dataset_df.to_dict("records")
collection.insert_many(documents)

print("Data ingestion into MongoDB completed")