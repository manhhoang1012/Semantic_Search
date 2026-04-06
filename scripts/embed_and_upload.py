import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from backend.services.embedding_service import embed_text
from backend.repositories.vector_repository import upsert_vectors

df = pd.read_csv("data/processed/clean_data.csv")

vectors = []

for _, row in df.iterrows():
    vector = embed_text(row["title"])

    vectors.append((
        str(row["reddit_id"]),
        vector,
        {
            "title": row["title"],
            "subreddit": row["subreddit"],
            "score": int(row["score"]),
            "comments": int(row["number_of_comments"]),
            "username": row["username"]
        }
    ))

    # upsert theo batch
    if len(vectors) == 100:
        upsert_vectors(vectors)
        vectors = []

# upsert phần còn lại
if vectors:
    upsert_vectors(vectors)

print("✅ Upload to Pinecone done!")