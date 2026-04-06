from backend.services.pinecone_service import get_index

index = get_index()

def upsert_vectors(vectors):
    index.upsert(vectors=vectors)

def query_vectors(vector, top_k=5, filter=None):
    return index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True,
        filter=filter
    )

def delete_vector(id):
    index.delete(ids=[id])