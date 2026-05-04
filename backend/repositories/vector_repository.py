

from backend.services.pinecone_service import get_index
from backend.config import MODEL_DIMENSION

def upsert_vectors(vectors):
    index = get_index()
    index.upsert(vectors=vectors)

def query_vectors(vector, top_k=5, filter=None):
    index = get_index()
    return index.query(
        vector=vector,
        top_k=top_k,
        include_metadata=True,
        filter=filter
    )

def delete_vector(id):
    index = get_index()
    index.delete(ids=[id])

# 🔥 thêm mới
def get_all_vectors(limit=20, pagination_token=None):
    index = get_index()
    ids = []
    try:
        kwargs = {}
        if pagination_token:
            kwargs["pagination_token"] = pagination_token

        for id_chunk in index.list(**kwargs):
            ids.extend(id_chunk)
            if len(ids) >= limit:
                break
    except Exception:
        pass

    ids = ids[:limit]
    if not ids:
        return {"matches": []}

    fetch_response = index.fetch(ids=ids)
    
    matches = []
    for vec_id, data in fetch_response.get("vectors", {}).items():
        matches.append({
            "id": vec_id,
            "metadata": data.get("metadata", {})
        })
        
    return {"matches": matches}