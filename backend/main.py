"""
FastAPI application entry point
Replaces Flask with production-ready FastAPI setup
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi

from backend.config import CORS_ORIGINS, DEBUG, API_HOST, API_PORT, ENVIRONMENT
from backend.utils.logger import setup_logging, get_logger
from backend.api.search_api import router as search_router
from backend.api.crud_api import router as crud_router
from backend.schemas import ErrorResponse, HealthCheckResponse

# Setup logging
setup_logging()
logger = get_logger(__name__)


# ============================================================================
# LIFESPAN EVENTS (FastAPI 0.93+)
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle.
    Startup: Initialize resources
    Shutdown: Cleanup
    """
    # Startup
    logger.info(f"Starting application in {ENVIRONMENT} environment")
    logger.info(f"CORS origins: {CORS_ORIGINS}")

    # Initialize embedding service on startup
    try:
        from backend.services.embedding_service import get_embedding_service

        service = await get_embedding_service()
        logger.info("Embedding service initialized")
    except Exception as e:
        logger.error(f"Failed to initialize embedding service: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application")


# ============================================================================
# CREATE FASTAPI APP
# ============================================================================

app = FastAPI(
    title="Pinecone Semantic Search API",
    description="Production-ready semantic search with Pinecone and FastAPI",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# ============================================================================
# MIDDLEWARE
# ============================================================================


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with latency"""
    start_time = time.time()
    request_id = request.headers.get("x-request-id", str(time.time()))

    # Add request ID to state for use in handlers
    request.state.request_id = request_id

    try:
        response = await call_next(request)
        process_time = time.time() - start_time

        logger.info(
            f"{request.method} {request.url.path} - "
            f"status={response.status_code} - latency={process_time*1000:.2f}ms"
        )

        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        return response

    except Exception as e:
        process_time = time.time() - start_time
        logger.error(
            f"{request.method} {request.url.path} - "
            f"error={str(e)} - latency={process_time*1000:.2f}ms",
            exc_info=True,
        )
        raise


# ============================================================================
# EXCEPTION HANDLERS
# ============================================================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail or "An error occurred",
            "status_code": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "status_code": 500,
        },
    )


# ============================================================================
# ROUTES
# ============================================================================


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for load balancers"""
    try:
        from backend.services.pinecone_service import get_index

        get_index()
        pinecone_status = "connected"
    except Exception as e:
        logger.warning(f"Pinecone health check failed: {str(e)}")
        pinecone_status = "disconnected"

    return HealthCheckResponse(
        status="healthy" if pinecone_status == "connected" else "degraded",
        pinecone_status=pinecone_status,
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Pinecone Semantic Search API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health",
    }


# Include routers
app.include_router(search_router, prefix="/api")
app.include_router(crud_router, prefix="/api")


# ============================================================================
# CUSTOM OPENAPI SCHEMA
# ============================================================================


def custom_openapi():
    """Customize OpenAPI schema"""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Pinecone Semantic Search API",
        version="1.0.0",
        description="Production-ready semantic search with Pinecone and FastAPI",
        routes=app.routes,
    )

    openapi_schema["info"]["x-logo"] = {
        "url": "https://pinecone.io/assets/pinecone-logo.svg"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# ============================================================================
# MAIN
# ============================================================================


if __name__ == "__main__":
    import uvicorn

    logger.info(
        f"Starting server on {API_HOST}:{API_PORT} with {API_HOST} workers"
    )
    uvicorn.run(
        "backend.main:app",
        host=API_HOST,
        port=API_PORT,
        workers=1,  # Use 1 for development, increase for production
        reload=DEBUG,
        log_level=logging.DEBUG if DEBUG else logging.INFO,
    )
