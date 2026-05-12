"""
Production-grade configuration management
Supports environment-based configs for dev/staging/prod
"""

from dotenv import load_dotenv
import os
from typing import Literal

load_dotenv()

# ============================================================================
# ENVIRONMENT & MODE
# ============================================================================
ENVIRONMENT: Literal["development", "staging", "production"] = os.getenv(
    "ENVIRONMENT", "development"
)
DEBUG: bool = ENVIRONMENT == "development"

# ============================================================================
# PINECONE CONFIGURATION
# ============================================================================
PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY", "")
PINECONE_ENV: str = os.getenv("PINECONE_ENV", "")
INDEX_NAME: str = os.getenv("INDEX_NAME", "default-index")
MODEL_NAME: str = os.getenv("MODEL_NAME", "paraphrase-multilingual-MiniLM-L12-v2")
MODEL_DIMENSION: int = int(os.getenv("MODEL_DIMENSION", "384"))

# ============================================================================
# EMBEDDING SERVICE CONFIGURATION
# ============================================================================
# Thread pool for blocking operations
EMBEDDING_MAX_WORKERS: int = int(os.getenv("EMBEDDING_MAX_WORKERS", "4"))

# Batch processing configuration
EMBEDDING_BATCH_SIZE: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
EMBEDDING_BATCH_TIMEOUT_MS: int = int(
    os.getenv("EMBEDDING_BATCH_TIMEOUT_MS", "100")
)  # Wait up to 100ms for batch to fill

# ============================================================================
# CHUNKING CONFIGURATION
# ============================================================================
CHUNKING_MAX_LENGTH: int = int(os.getenv("CHUNKING_MAX_LENGTH", "500"))
CHUNKING_OVERLAP: int = int(os.getenv("CHUNKING_OVERLAP", "50"))

# ============================================================================
# API CONFIGURATION
# ============================================================================
API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
API_PORT: int = int(os.getenv("API_PORT", "5000"))
API_WORKERS: int = int(os.getenv("API_WORKERS", "4"))

# CORS Configuration
CORS_ORIGINS: list[str] = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
).split(",")

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO" if not DEBUG else "DEBUG")
LOG_FORMAT: str = os.getenv(
    "LOG_FORMAT", "json"
)  # "json" for production, "text" for development

# ============================================================================
# RATE LIMITING
# ============================================================================
RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
RATE_LIMIT_REQUESTS_PER_MINUTE: int = int(
    os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60")
)

# ============================================================================
# CACHING (Redis - optional)
# ============================================================================
REDIS_ENABLED: bool = os.getenv("REDIS_ENABLED", "false").lower() == "true"
REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

# ============================================================================
# VALIDATION
# ============================================================================
if not PINECONE_API_KEY:
    raise ValueError("PINECONE_API_KEY is required")
if not INDEX_NAME:
    raise ValueError("INDEX_NAME is required")