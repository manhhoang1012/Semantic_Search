
"""
Vector repository for Pinecone operations
Handles all vector DB CRUD operations with proper error handling
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from backend.services.pinecone_service import get_index
from backend.config import MODEL_DIMENSION

logger = logging.getLogger(__name__)


async def upsert_vectors(
    vectors: List[Tuple[str, List[float], Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    Upsert vectors to Pinecone.

    Args:
        vectors: List of (id, vector, metadata) tuples

    Returns:
        Response from Pinecone

    Raises:
        ValueError: If vectors list is empty
        Exception: If Pinecone operation fails
    """
    if not vectors:
        raise ValueError("Vectors list cannot be empty")

    try:
        index = get_index()
        response = index.upsert(vectors=vectors)
        logger.debug(f"Upserted {len(vectors)} vectors to Pinecone")
        return {"success": True, "upserted_count": len(vectors)}
    except Exception as e:
        logger.error(f"Error upserting vectors: {str(e)}")
        raise


async def query_vectors(
    vector: List[float],
    top_k: int = 5,
    filter: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Query vectors from Pinecone.

    Args:
        vector: Query vector
        top_k: Number of top results to return
        filter: Optional metadata filter

    Returns:
        Query results with matches

    Raises:
        ValueError: If vector is invalid
        Exception: If Pinecone operation fails
    """
    if not vector or len(vector) == 0:
        raise ValueError("Query vector cannot be empty")

    if len(vector) != MODEL_DIMENSION:
        raise ValueError(f"Vector dimension {len(vector)} != {MODEL_DIMENSION}")

    try:
        index = get_index()
        results = index.query(
            vector=vector, top_k=top_k, include_metadata=True, filter=filter
        )
        logger.debug(f"Query returned {len(results.get('matches', []))} matches")
        return results
    except Exception as e:
        logger.error(f"Error querying vectors: {str(e)}")
        raise


async def delete_vector(id: str) -> Dict[str, Any]:
    """
    Delete a single vector by ID.

    Args:
        id: Vector ID to delete

    Returns:
        Deletion result

    Raises:
        ValueError: If ID is empty
        Exception: If Pinecone operation fails
    """
    if not id or not id.strip():
        raise ValueError("Vector ID cannot be empty")

    try:
        index = get_index()
        index.delete(ids=[id])
        logger.debug(f"Deleted vector: {id}")
        return {"success": True, "deleted_count": 1}
    except Exception as e:
        logger.error(f"Error deleting vector {id}: {str(e)}")
        raise


async def delete_vectors_by_parent_id(parent_id: str) -> Dict[str, Any]:
    """
    Delete all vectors (chunks) associated with a parent document.

    This function queries for all chunk IDs with the given parent_id,
    then deletes them. This is more robust than hardcoding a range.

    Args:
        parent_id: Parent document ID

    Returns:
        Deletion result

    Raises:
        ValueError: If parent_id is empty
        Exception: If Pinecone operation fails
    """
    if not parent_id or not parent_id.strip():
        raise ValueError("Parent ID cannot be empty")

    try:
        index = get_index()
        ids_to_delete = []

        # Fetch all vector IDs (Note: Pinecone's list operation doesn't support filters)
        # Alternative: maintain a separate index or metadata store
        # For now, we'll fetch all and filter in application
        logger.debug(f"Fetching vectors for parent_id: {parent_id}")

        for id_chunk in index.list():
            ids_to_delete.extend(id_chunk)

        # Filter for matching parent_id
        # Fetch metadata for these IDs to check parent_id
        matching_ids = [parent_id]  # Always include the parent ID itself

        if ids_to_delete:
            # Fetch in batches to check metadata
            batch_size = 100
            for i in range(0, len(ids_to_delete), batch_size):
                batch_ids = ids_to_delete[i : i + batch_size]
                try:
                    fetch_response = index.fetch(ids=batch_ids)
                    for vec_id, data in fetch_response.get("vectors", {}).items():
                        metadata = data.get("metadata", {})
                        if metadata.get("parent_id") == parent_id and vec_id not in matching_ids:
                            matching_ids.append(vec_id)
                except Exception as e:
                    logger.warning(f"Error fetching metadata for batch: {str(e)}")

        # Delete all matching vectors
        if matching_ids:
            logger.debug(f"Deleting {len(matching_ids)} vectors for parent_id: {parent_id}")
            index.delete(ids=matching_ids)

        logger.info(
            f"Successfully deleted {len(matching_ids)} vectors for parent_id: {parent_id}"
        )
        return {"success": True, "deleted_count": len(matching_ids), "ids": matching_ids}

    except Exception as e:
        logger.error(f"Error deleting vectors by parent_id {parent_id}: {str(e)}")
        raise


async def get_stats() -> Dict[str, Any]:
    """
    Get index statistics.

    Returns:
        Index statistics

    Raises:
        Exception: If Pinecone operation fails
    """
    try:
        index = get_index()
        stats = index.describe_index_stats()

        # Convert response to dict
        if hasattr(stats, "to_dict"):
            return stats.to_dict()
        return dict(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise


async def get_all_vectors(
    limit: int = 20, pagination_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get all vectors with pagination.

    Args:
        limit: Maximum number of vectors to return
        pagination_token: Token for pagination

    Returns:
        Vectors and next pagination token

    Raises:
        Exception: If Pinecone operation fails
    """
    try:
        index = get_index()
        ids = []
        next_token = None

        # Build kwargs for pagination
        kwargs = {}
        if pagination_token:
            kwargs["pagination_token"] = pagination_token

        # List all IDs
        for id_chunk in index.list(**kwargs):
            ids.extend(id_chunk)
            if len(ids) >= limit:
                break

        ids = ids[:limit]
        logger.debug(f"Listed {len(ids)} vector IDs")

        if not ids:
            return {"matches": [], "pagination_token": None}

        # Fetch vectors with metadata
        fetch_response = index.fetch(ids=ids)

        matches = []
        for vec_id, data in fetch_response.get("vectors", {}).items():
            matches.append({"id": vec_id, "metadata": data.get("metadata", {})})

        return {"matches": matches, "pagination_token": next_token}

    except Exception as e:
        logger.error(f"Error getting all vectors: {str(e)}")
        raise