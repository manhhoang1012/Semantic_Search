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

crud_bp = Blueprint("crud", __name__)

# ➕ ADD / UPDATE
@crud_bp.route("/add", methods=["POST"])
def add():
    data = request.json

    vector = embed_text(data["title"])

    upsert_vectors([(
        data["id"],
        vector,
        data
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
    results = get_all_vectors()

    output = []
    for item in results["matches"]:
        output.append({
            "id": item["id"],
            "metadata": item["metadata"]
        })

    return jsonify(output)