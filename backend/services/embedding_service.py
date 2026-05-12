"""
Async embedding service with batch processing
Handles efficient embedding generation with GPU/CPU optimization
"""

import asyncio
import logging
from typing import List
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor
from backend.config import (
    MODEL_NAME,
    EMBEDDING_MAX_WORKERS,
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_BATCH_TIMEOUT_MS,
)

logger = logging.getLogger(__name__)


class AsyncEmbeddingService:
    """
    Async embedding service with batch processing.

    Features:
    - Singleton pattern to avoid loading model multiple times
    - Batch processing to maximize GPU/CPU utilization
    - Async/await interface for non-blocking calls
    - Thread pooling for blocking SentenceTransformers calls
    """

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the embedding service"""
        if hasattr(self, "_initialized"):
            return

        self._model: SentenceTransformer = None
        self._executor = ThreadPoolExecutor(max_workers=EMBEDDING_MAX_WORKERS)
        self._batch_queue: List[dict] = []
        self._batch_lock = asyncio.Lock()
        self._batch_event = asyncio.Event()
        self._initialized = True
        self._batch_task = None

        logger.info(
            f"AsyncEmbeddingService initialized with model={MODEL_NAME}, "
            f"max_workers={EMBEDDING_MAX_WORKERS}, batch_size={EMBEDDING_BATCH_SIZE}"
        )

    def _get_model(self) -> SentenceTransformer:
        """Load model (thread-safe)"""
        if self._model is None:
            logger.info(f"Loading embedding model: {MODEL_NAME}")
            self._model = SentenceTransformer(MODEL_NAME)
            logger.info(f"Model loaded successfully")
        return self._model

    async def embed(self, text: str) -> List[float]:
        """
        Embed a single text asynchronously using batch processing.

        Args:
            text: Text to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty for embedding")

        # Create future to track completion
        future = asyncio.Future()

        async with self._batch_lock:
            self._batch_queue.append({"text": text, "future": future})

            # Start batch processor if not running
            if self._batch_task is None or self._batch_task.done():
                self._batch_task = asyncio.create_task(self._process_batch())

            # If batch is full, trigger processing immediately
            if len(self._batch_queue) >= EMBEDDING_BATCH_SIZE:
                self._batch_event.set()

        # Wait for this item to be processed
        try:
            result = await asyncio.wait_for(
                future, timeout=(EMBEDDING_BATCH_TIMEOUT_MS / 1000.0) * 2
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Timeout waiting for embedding of text: {text[:50]}...")
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Embed multiple texts at once (more efficient than individual calls).

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors

        Raises:
            ValueError: If texts list is empty
        """
        if not texts:
            raise ValueError("Texts list cannot be empty")

        # Validate all texts
        for text in texts:
            if not text or not text.strip():
                raise ValueError("All texts must be non-empty")

        logger.debug(f"Batch embedding {len(texts)} texts")

        # Use executor to run blocking embedding operation
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(
            self._executor, self._embed_texts_blocking, texts
        )

        logger.debug(f"Batch embedding complete for {len(texts)} texts")
        return embeddings

    def _embed_texts_blocking(self, texts: List[str]) -> List[List[float]]:
        """
        Blocking embedding operation (runs in thread pool).

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        model = self._get_model()
        embeddings = model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()

    async def _process_batch(self) -> None:
        """
        Process queued embeddings in batches.
        Waits for batch to fill or timeout.
        """
        while True:
            # Wait for either batch to fill or timeout
            try:
                await asyncio.wait_for(
                    self._batch_event.wait(),
                    timeout=EMBEDDING_BATCH_TIMEOUT_MS / 1000.0,
                )
                self._batch_event.clear()
            except asyncio.TimeoutError:
                # Timeout reached, process whatever is queued
                pass

            async with self._batch_lock:
                if not self._batch_queue:
                    # No items to process
                    break

                # Extract batch
                batch = self._batch_queue[: EMBEDDING_BATCH_SIZE]
                self._batch_queue = self._batch_queue[EMBEDDING_BATCH_SIZE :]
                texts = [item["text"] for item in batch]

            try:
                # Embed texts (blocking, runs in executor)
                loop = asyncio.get_event_loop()
                embeddings = await loop.run_in_executor(
                    self._executor, self._embed_texts_blocking, texts
                )

                # Distribute results to futures
                for item, embedding in zip(batch, embeddings):
                    if not item["future"].done():
                        item["future"].set_result(embedding)

                logger.debug(f"Processed batch of {len(batch)} texts")

            except Exception as e:
                logger.error(f"Error processing batch: {str(e)}")
                # Set exception on all futures in batch
                for item in batch:
                    if not item["future"].done():
                        item["future"].set_exception(e)

            # If more items queued, continue loop
            async with self._batch_lock:
                if not self._batch_queue:
                    break


# Singleton instance
_embedding_service: AsyncEmbeddingService = None


async def get_embedding_service() -> AsyncEmbeddingService:
    """Get singleton embedding service instance"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = AsyncEmbeddingService()
    return _embedding_service


async def embed_text(text: str) -> List[float]:
    """
    Convenience function to embed a single text.

    Args:
        text: Text to embed

    Returns:
        List of floats representing the embedding vector
    """
    service = await get_embedding_service()
    return await service.embed(text)


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Convenience function to embed multiple texts.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    service = await get_embedding_service()
    return await service.embed_batch(texts)