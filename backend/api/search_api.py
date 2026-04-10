from flask import Blueprint, request, jsonify
from backend.services.embedding_service import embed_text
from backend.repositories.vector_repository import query_vectors
import time

search_bp = Blueprint("search", __name__)

@search_bp.route("/search", methods=["POST"])
def search():
    start_time = time.time()
    data = request.json
    query = data.get("query")
    top_k = data.get("top_k", 5)
    filter_data = data.get("filter", None)

    vector = embed_text(query)

    results = query_vectors(vector, top_k, filter_data)

    output = []
    for match in results["matches"]:
        output.append({
            "id": match["id"],
            "score": match["score"],
            "metadata": match["metadata"]
        })
    

    end_time = time.time()

    latency = end_time - start_time

    return jsonify({
    "results": output,
    "latency": latency
})