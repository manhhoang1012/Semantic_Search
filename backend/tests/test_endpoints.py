"""
Test suite for FastAPI endpoints
Run with: pytest -v
"""

import pytest
from httpx import AsyncClient
from backend.main import app
from backend.schemas import SearchRequest, AddDataRequest


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]


@pytest.mark.asyncio
async def test_root():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


@pytest.mark.asyncio
async def test_search_missing_query():
    """Test search with missing query"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/search/search", json={"query": ""})
        assert response.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_add_data_validation():
    """Test add data endpoint validation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Missing required title field
        response = await client.post("/api/data/add", json={"content": "test"})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_add_data_success():
    """Test successful add data"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        payload = {
            "title": "Test Document",
            "content": "This is a test document with some content to embed.",
            "subreddit": "test",
            "score": 100,
        }
        response = await client.post("/api/data/add", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "id" in data
        assert "chunks_created" in data


@pytest.mark.asyncio
async def test_stats():
    """Test stats endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/data/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_vector_count" in data
        assert "dimension" in data


@pytest.mark.asyncio
async def test_list_data():
    """Test list endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/data/list?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total_returned" in data
        assert "latency_ms" in data
