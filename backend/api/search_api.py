from flask import Blueprint, request, jsonify
from backend.services.embedding_service import embed_text
from backend.repositories.vector_repository import query_vectors
from backend.models.post_model import Post
import time

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["POST"])
def search():
    start_time = time.time()
    data = request.json
    
    query = data.get("query")
    if not query:
        return jsonify({"error": "Missing search query"}), 400
        
    # Lấy giá trị top_k từ request, mặc định là 5 nếu không có
    try:
        top_k = int(data.get("top_k", 5))
    except (ValueError, TypeError):
        top_k = 5
        
    filter_data = data.get("filter", None)

    vector = embed_text(query)

    # Truyền top_k * 3 vào vector_repository để đảm bảo có đủ document sau khi group
    fetch_k = top_k * 3
    results = query_vectors(vector, fetch_k, filter_data)

    grouped_output = {}
    for match in results.get("matches", []):
        meta = match.get("metadata", {})
        parent_id = meta.get("parent_id", match["id"]) # Fallback to id if parent_id is missing

        # Only keep the best chunk for each parent_id
        if parent_id not in grouped_output:
            post = Post(
                id=parent_id,
                title=meta.get("title", ""),
                content=meta.get("content", ""),
                subreddit=meta.get("subreddit", ""),
                score=meta.get("score", 0),
                comments=meta.get("comments", 0),
                username=meta.get("username", ""),
                parent_id=parent_id,
                chunk_index=meta.get("chunk_index", 0)
            )
            grouped_output[parent_id] = {
                "id": post.id,
                "score": match["score"],
                "metadata": post.to_dict()
            }
            
        if len(grouped_output) >= top_k:
            break

    output = list(grouped_output.values())
    

    end_time = time.time()

    latency = end_time - start_time

    return jsonify({
    "results": output,
    "latency": latency
})