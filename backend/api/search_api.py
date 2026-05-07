"""
FastAPI router for semantic search operations
"""

import logging
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from backend.schemas import (
    SearchRequest,
    SearchResponse,
    SearchResult,
    SearchResultMetadata,
    ErrorResponse,
)
from backend.services.embedding_service import embed_text
from backend.repositories.vector_repository import query_vectors
from backend.models.post_model import Post
router = APIRouter()

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.post(
    "/search",
    response_model=SearchResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def search(request: SearchRequest) -> SearchResponse:
    """
    Semantic search across indexed documents.

    This endpoint:
    1. Embeds the query using SentenceTransformers
    2. Queries Pinecone for similar vectors
    3. Groups results by parent_id (returns best chunk per document)
    4. Returns top_k unique documents

    Args:
        request: Search request with query, top_k, and optional filter

    Returns:
        SearchResponse with matching documents and latency

    Raises:
        HTTPException: On validation or search errors
    """
    start_time = time.time()
    request_id = None

    try:
        # Log request
        logger.info(
            f"Search request: query_length={len(request.query)}, top_k={request.top_k}"
        )

        # Embed query
        logger.debug("Embedding query...")
        vector = await embed_text(request.query)

        # Query Pinecone (fetch more to account for chunk grouping)
        fetch_k = request.top_k * 3
        logger.debug(f"Querying Pinecone with top_k={fetch_k}")

        results = await query_vectors(vector, fetch_k, request.filter)

        # Group results by parent_id (deduplicate chunks)
        grouped_output = {}
        for match in results.get("matches", []):
            meta = match.get("metadata", {})
            parent_id = meta.get("parent_id", match["id"])

            # Keep only best chunk for each parent document
            if parent_id not in grouped_output:
                post = Post(
                    id=parent_id,
                    title=meta.get("title", ""),
                    content=meta.get("content", ""),
                    subreddit=meta.get("subreddit"),
                    score=meta.get("score", 0),
                    comments=meta.get("comments", 0),
                    username=meta.get("username"),
                    parent_id=parent_id,
                    chunk_index=meta.get("chunk_index", 0),
                    category=meta.get("category"),
                    author=meta.get("author"),
                )
                grouped_output[parent_id] = SearchResult(
                    id=post.id,
                    score=match.get("score", 0.0),
                    metadata=SearchResultMetadata(**post.to_dict()),
                )

            if len(grouped_output) >= request.top_k:
                break

        latency_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Search completed: results={len(grouped_output)}, latency_ms={latency_ms:.2f}"
        )

        return SearchResponse(
            results=list(grouped_output.values()),
            latency_ms=latency_ms,
            total_results=len(grouped_output),
        )

    except ValueError as e:
        logger.warning(f"Validation error in search: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in search endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during search",
        )