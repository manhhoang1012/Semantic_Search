# from flask import Blueprint, request, jsonify
# from backend.services.embedding_service import embed_text
# from backend.repositories.vector_repository import upsert_vectors, delete_vector

# crud_bp = Blueprint("crud", __name__)

# @crud_bp.route("/add", methods=["POST"])
# def add():
#     data = request.json

#     vector = embed_text(data["title"])

#     upsert_vectors([(
#         data["id"],
#         vector,
#         data
#     )])

#     return jsonify({"message": "Added!"})


# @crud_bp.route("/delete/<id>", methods=["DELETE"])
# def delete(id):
#     delete_vector(id)
#     return jsonify({"message": "Deleted!"})

from flask import Blueprint, request, jsonify
from backend.services.embedding_service import embed_text
from backend.repositories.vector_repository import (
    upsert_vectors,
    delete_vector,
    get_all_vectors
)
from backend.models.post_model import Post

crud_bp = Blueprint("crud", __name__)

# ➕ ADD / UPDATE
@crud_bp.route("/add", methods=["POST"])
def add():
    data = request.json
    
    try:
        post = Post(
            id=data["id"],
            title=data["title"],
            subreddit=data.get("subreddit", ""),
            score=data.get("score", 0),
            comments=data.get("comments", 0),
            username=data.get("username", "")
        )
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400

    vector = embed_text(post.title)

    upsert_vectors([(
        str(post.id),
        vector,
        post.to_dict()
    )])

    return jsonify({"message": "Saved!"})


# ❌ DELETE
@crud_bp.route("/delete/<id>", methods=["DELETE"])
def delete(id):
    delete_vector(id)
    return jsonify({"message": "Deleted!"})


# 📋 LIST DATA
@crud_bp.route("/list", methods=["GET"])
def get_list():
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        limit = 20
        
    pagination_token = request.args.get("pagination_token")

    results = get_all_vectors(limit=limit, pagination_token=pagination_token)

    output = []
    for item in results.get("matches", []):
        meta = item.get("metadata", {})
        post = Post(
            id=item["id"],
            title=meta.get("title", ""),
            subreddit=meta.get("subreddit", ""),
            score=meta.get("score", 0),
            comments=meta.get("comments", 0),
            username=meta.get("username", "")
        )
        output.append({
            "id": post.id,
            "metadata": post.to_dict()
        })

    return jsonify(output)