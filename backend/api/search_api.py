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

    # Truyền top_k vào vector_repository
    results = query_vectors(vector, top_k, filter_data)

    output = []
    for match in results.get("matches", []):
        meta = match.get("metadata", {})
        post = Post(
            id=match["id"],
            title=meta.get("title", ""),
            content=meta.get("content", ""),
            subreddit=meta.get("subreddit", ""),
            score=meta.get("score", 0),
            comments=meta.get("comments", 0),
            username=meta.get("username", "")
        )
        output.append({
            "id": post.id,
            "score": match["score"],
            "metadata": post.to_dict()
        })
    

    end_time = time.time()

    latency = end_time - start_time

    return jsonify({
    "results": output,
    "latency": latency
})