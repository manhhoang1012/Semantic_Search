from pinecone import Pinecone, ServerlessSpec
from backend.config import PINECONE_API_KEY, INDEX_NAME

pc = Pinecone(api_key=PINECONE_API_KEY)

def create_index_if_not_exists(dimension=384):
    if INDEX_NAME not in [i["name"] for i in pc.list_indexes()]:
        pc.create_index(
            name=INDEX_NAME,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

def get_index():
    return pc.Index(INDEX_NAME)