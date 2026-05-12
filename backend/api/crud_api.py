"""
FastAPI router for CRUD operations on vector database
"""

import logging
import time
import uuid

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from backend.schemas import (
    AddDataRequest,
    AddDataResponse,
    DeleteResponse,
    ListDataResponse,
    StatsResponse,
    ErrorResponse,
)
from backend.services.embedding_service import embed_texts, embed_text
from backend.repositories.vector_repository import (
    upsert_vectors,
    delete_vectors_by_parent_id,
    get_all_vectors,
    get_stats,
)
from backend.models.post_model import Post
from backend.services.chunking_service import chunk_text

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/data", tags=["crud"])


@router.get("/stats", response_model=StatsResponse)
async def stats() -> StatsResponse:
    """
    Get database statistics.

    Returns:
        Index statistics including total vector count and dimensions
    """
    try:
        logger.debug("Fetching statistics")
        stats_dict = await get_stats()

        return StatsResponse(
            total_vector_count=stats_dict.get("total_vector_count", 0),
            dimension=stats_dict.get("dimension", 384),
            index_fullness=stats_dict.get("index_fullness", 0.0),
        )
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch statistics")


@router.post(
    "/add",
    response_model=AddDataResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def add(request: AddDataRequest) -> AddDataResponse:
    """
    Add or update a document in the vector database.

    This endpoint:
    1. Validates input using Pydantic
    2. Chunks content into semantic pieces
    3. Embeds all chunks using batch processing
    4. Upserts vectors and metadata to Pinecone

    Args:
        request: Document data including title, content, and metadata

    Returns:
        AddDataResponse with chunk count and processing latency

    Raises:
        HTTPException: On validation or processing errors
    """
    start_time = time.time()

    try:
        parent_id = request.id or str(uuid.uuid4())
        title = request.title
        content = request.content
        subreddit = request.subreddit or ""
        score = request.score
        comments = request.comments
        username = request.username or ""
        category = request.category or ""
        author = request.author or ""

        logger.info(
            f"Adding document: id={parent_id}, title={title[:50]}..., "
            f"content_length={len(content)}"
        )

        # Chunk content
        text_to_chunk = content if content else title
        chunks = chunk_text(text_to_chunk)
        if not chunks:
            chunks = [title]

        logger.debug(f"Chunked document into {len(chunks)} chunks")

        # Prepare texts for batch embedding
        texts_to_embed = [f"{title}. {chunk}" for chunk in chunks]

        # Batch embed all chunks
        logger.debug(f"Embedding {len(texts_to_embed)} chunks")
        embeddings = await embed_texts(texts_to_embed)

        if len(embeddings) != len(chunks):
            raise RuntimeError(
                f"Embedding count mismatch: got {len(embeddings)}, "
                f"expected {len(chunks)}"
            )

        # Prepare vectors for upsert
        vectors_to_upsert = []
        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
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
                author=author,
            )

            vectors_to_upsert.append((str(post.id), embedding, post.to_dict()))

        # Upsert to Pinecone
        if vectors_to_upsert:
            logger.debug(f"Upserting {len(vectors_to_upsert)} vectors")
            await upsert_vectors(vectors_to_upsert)

        latency_ms = (time.time() - start_time) * 1000
        logger.info(
            f"Document added successfully: id={parent_id}, "
            f"chunks={len(vectors_to_upsert)}, latency_ms={latency_ms:.2f}"
        )

        return AddDataResponse(
            success=True,
            message="Document saved successfully",
            id=parent_id,
            chunks_created=len(vectors_to_upsert),
            latency_ms=latency_ms,
        )

    except ValueError as e:
        logger.warning(f"Validation error in add: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error adding document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to add document")


@router.delete(
    "/delete/{id}",
    response_model=DeleteResponse,
    responses={
        400: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
async def delete(id: str) -> DeleteResponse:
    """
    Delete a document and all its chunks from the vector database.

    This endpoint:
    1. Finds all chunks associated with the parent_id
    2. Deletes all vectors from Pinecone
    3. Returns deletion statistics

    Args:
        id: Parent document ID to delete

    Returns:
        DeleteResponse with count of deleted vectors

    Raises:
        HTTPException: On validation or deletion errors
    """
    start_time = time.time()

    try:
        if not id or not id.strip():
            raise ValueError("Document ID cannot be empty")

        logger.info(f"Deleting document: id={id}")

        result = await delete_vectors_by_parent_id(id)

        latency_ms = (time.time() - start_time) * 1000
        logger.info(f"Document deleted: id={id}, count={result['deleted_count']}")

        return DeleteResponse(
            success=True,
            message=f"Deleted {result['deleted_count']} vectors",
            ids_deleted=result["deleted_count"],
            latency_ms=latency_ms,
        )

    except ValueError as e:
        logger.warning(f"Validation error in delete: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete document")


@router.get(
    "/list",
    response_model=ListDataResponse,
    responses={
        500: {"model": ErrorResponse},
    },
)
async def list_data(
    limit: int = Query(default=20, ge=1, le=100),
    pagination_token: Optional[str] = Query(default=None),
) -> ListDataResponse:
    """
    List all documents with pagination.

    This endpoint:
    1. Fetches vectors with pagination
    2. Groups by parent_id to show unique documents
    3. Returns metadata for display

    Args:
        limit: Maximum number of unique documents to return (1-100)
        pagination_token: Token for pagination

    Returns:
        ListDataResponse with document metadata

    Raises:
        HTTPException: On query errors
    """
    start_time = time.time()

    try:
        logger.debug(f"Listing data: limit={limit}, token={'present' if pagination_token else 'none'}")

        # Fetch more vectors to account for grouping
        results = await get_all_vectors(
            limit=limit * 3, pagination_token=pagination_token
        )

        grouped_output = {}
        for item in results.get("matches", []):
            meta = item.get("metadata", {})
            parent_id = meta.get("parent_id", item["id"])

            # Keep only one chunk per parent
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
                grouped_output[parent_id] = post.to_dict()

            if len(grouped_output) >= limit:
                break

        items = list(grouped_output.values())
        latency_ms = (time.time() - start_time) * 1000

        logger.debug(f"Listed {len(items)} documents in {latency_ms:.2f}ms")

        return ListDataResponse(
            items=items,
            total_returned=len(items),
            latency_ms=latency_ms,
        )

    except Exception as e:
        logger.error(f"Error listing data: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to list data")