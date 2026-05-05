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
    get_all_vectors,
    get_stats,
    delete_vectors_by_parent_id
)
from backend.models.post_model import Post
from backend.services.chunking_service import chunk_text
import uuid

crud_bp = Blueprint("crud", __name__)

# 📊 STATS
@crud_bp.route("/stats", methods=["GET"])
def stats():
    return jsonify(get_stats())

# ➕ ADD / UPDATE
@crud_bp.route("/add", methods=["POST"])
def add():
    data = request.json
    
    try:
        parent_id = data.get("id") or str(uuid.uuid4())
        title = data["title"]
        content = data.get("content", "")
        subreddit = data.get("subreddit", "")
        score = data.get("score", 0)
        comments = data.get("comments", 0)
        username = data.get("username", "")
        category = data.get("category", "")
        author = data.get("author", "")
    except KeyError as e:
        return jsonify({"error": f"Missing required field: {e}"}), 400

    chunks = chunk_text(content, max_length=500, overlap=50) if content else [title]
    vectors_to_upsert = []
    
    for idx, chunk in enumerate(chunks):
        chunk_id = f"{parent_id}_{idx}"
        post = Post(
            id=chunk_id,
            title=title,
            content=chunk,
            subreddit=subreddit,
            score=score,
            comments=comments,
            username=username,
            parent_id=parent_id,
            chunk_index=idx,
            category=category,
            author=author
        )
        
        text_to_embed = f"{title}. {chunk}"
        vector = embed_text(text_to_embed)
        
        vectors_to_upsert.append((
            str(post.id),
            vector,
            post.to_dict()
        ))

    if vectors_to_upsert:
        upsert_vectors(vectors_to_upsert)

    return jsonify({"message": "Saved!", "chunks_created": len(vectors_to_upsert)})


# ❌ DELETE
@crud_bp.route("/vectors/<id>", methods=["DELETE"])
def delete(id):
    delete_vectors_by_parent_id(id)
    return jsonify({"message": "Deleted!"})


# 📋 LIST DATA
@crud_bp.route("/list", methods=["GET"])
def get_list():
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        limit = 20
        
    pagination_token = request.args.get("pagination_token")

    # Fetch more vectors so we have enough unique documents
    results = get_all_vectors(limit=limit * 3, pagination_token=pagination_token)

    grouped_output = {}
    
    for item in results.get("matches", []):
        meta = item.get("metadata", {})
        parent_id = meta.get("parent_id", item["id"])
        
        if parent_id not in grouped_output:
            post = Post(
                id=parent_id, # UI will use parent_id to delete
                title=meta.get("title", ""),
                content=meta.get("content", ""),
                subreddit=meta.get("subreddit", ""),
                score=meta.get("score", 0),
                comments=meta.get("comments", 0),
                username=meta.get("username", ""),
                parent_id=parent_id,
                chunk_index=meta.get("chunk_index", 0),
                category=meta.get("category", ""),
                author=meta.get("author", "")
            )
            grouped_output[parent_id] = {
                "id": post.id,
                "metadata": post.to_dict()
            }
            
        if len(grouped_output) >= limit:
            break

    return jsonify(list(grouped_output.values()))