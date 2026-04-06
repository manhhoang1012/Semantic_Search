from flask import Blueprint, request, jsonify
from backend.services.embedding_service import embed_text
from backend.repositories.vector_repository import upsert_vectors, delete_vector

crud_bp = Blueprint("crud", __name__)

@crud_bp.route("/add", methods=["POST"])
def add():
    data = request.json

    vector = embed_text(data["title"])

    upsert_vectors([(
        data["id"],
        vector,
        data
    )])

    return jsonify({"message": "Added!"})


@crud_bp.route("/delete/<id>", methods=["DELETE"])
def delete(id):
    delete_vector(id)
    return jsonify({"message": "Deleted!"})