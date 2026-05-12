"""
Pydantic models for request/response validation
Provides strict type checking and automatic documentation
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Any
from uuid import uuid4


# ============================================================================
# SEARCH ENDPOINT SCHEMAS
# ============================================================================


class SearchRequest(BaseModel):
    """Schema for search endpoint"""

    query: str = Field(
        ..., min_length=1, max_length=2000, description="Search query text"
    )
    top_k: int = Field(
        default=5, ge=1, le=100, description="Number of top results to return"
    )
    filter: Optional[dict[str, Any]] = Field(
        default=None, description="Pinecone metadata filter"
    )

    @field_validator("query")
    @classmethod
    def query_strip(cls, v: str) -> str:
        """Strip whitespace from query"""
        return v.strip()


class SearchResultMetadata(BaseModel):
    """Metadata for a single search result"""

    id: str
    title: str
    content: str
    subreddit: Optional[str] = None
    score: int = 0
    comments: int = 0
    username: Optional[str] = None
    parent_id: str
    chunk_index: int = 0
    category: Optional[str] = None
    author: Optional[str] = None


class SearchResult(BaseModel):
    """Single result in search response"""

    id: str
    score: float = Field(description="Similarity score from 0-1")
    metadata: SearchResultMetadata


class SearchResponse(BaseModel):
    """Response for search endpoint"""

    results: List[SearchResult]
    latency_ms: float = Field(description="Query latency in milliseconds")
    total_results: int = Field(description="Total unique documents found")


# ============================================================================
# ADD/UPDATE ENDPOINT SCHEMAS
# ============================================================================


class AddDataRequest(BaseModel):
    """Schema for adding/updating data"""

    id: Optional[str] = Field(
        default_factory=lambda: str(uuid4()),
        description="Optional custom ID; auto-generated if not provided",
    )
    title: str = Field(..., min_length=1, max_length=1000, description="Document title")
    content: str = Field(
        default="", max_length=100000, description="Document content to embed and chunk"
    )
    subreddit: Optional[str] = Field(default="", max_length=100)
    score: int = Field(default=0, ge=0, description="Post score/karma")
    comments: int = Field(default=0, ge=0, description="Number of comments")
    username: Optional[str] = Field(default="", max_length=100)
    category: Optional[str] = Field(default="", max_length=100)
    author: Optional[str] = Field(default="", max_length=100)

    @field_validator("title")
    @classmethod
    def title_strip(cls, v: str) -> str:
        """Strip whitespace"""
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty or whitespace-only")
        return v


class AddDataResponse(BaseModel):
    """Response for add endpoint"""

    success: bool
    message: str
    id: str
    chunks_created: int
    latency_ms: float


# ============================================================================
# DELETE ENDPOINT SCHEMAS
# ============================================================================


class DeleteResponse(BaseModel):
    """Response for delete endpoint"""

    success: bool
    message: str
    ids_deleted: int
    latency_ms: float


# ============================================================================
# LIST ENDPOINT SCHEMAS
# ============================================================================


class ListDataResponse(BaseModel):
    """Response for list endpoint"""

    items: List[SearchResultMetadata]
    total_returned: int
    latency_ms: float


# ============================================================================
# STATS ENDPOINT SCHEMAS
# ============================================================================


class StatsResponse(BaseModel):
    """Response for stats endpoint"""

    total_vector_count: int = Field(description="Total vectors in index")
    dimension: int = Field(description="Vector dimension")
    index_fullness: float = Field(description="Index fullness percentage (0-1)")


# ============================================================================
# ERROR RESPONSE SCHEMAS
# ============================================================================


class ErrorResponse(BaseModel):
    """Standard error response"""

    success: bool = False
    error: str
    detail: Optional[str] = None
    status_code: int


# ============================================================================
# HEALTH CHECK SCHEMA
# ============================================================================


class HealthCheckResponse(BaseModel):
    """Health check response"""

    status: str = "healthy"
    version: str = "1.0.0"
    pinecone_status: str = Field(description="'connected' or 'disconnected'")
