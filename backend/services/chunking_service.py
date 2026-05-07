"""
Text chunking service with overlap support
Splits documents into semantic chunks for better embedding
"""

import logging
from typing import List
from backend.config import CHUNKING_MAX_LENGTH, CHUNKING_OVERLAP

logger = logging.getLogger(__name__)


def chunk_text(
    text: str,
    max_length: int = CHUNKING_MAX_LENGTH,
    overlap: int = CHUNKING_OVERLAP,
) -> List[str]:
    """
    Split text into chunks with overlap.

    This function intelligently chunks text by looking for natural breaking
    points (periods, exclamation marks, etc.) to maintain semantic coherence.

    Args:
        text: Text to chunk
        max_length: Maximum characters per chunk (default: 500)
        overlap: Number of overlapping characters between chunks (default: 50)

    Returns:
        List of text chunks

    Raises:
        ValueError: If text is empty or chunk parameters are invalid
    """
    if not text:
        logger.warning("Empty text provided to chunk_text")
        return []

    if max_length <= 0:
        raise ValueError("max_length must be positive")

    if overlap < 0 or overlap >= max_length:
        raise ValueError("overlap must be between 0 and max_length")

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + max_length

        # If we're not at the end, find a natural breaking point
        if end < text_length:
            break_point = end
            # Look for sentence-ending punctuation
            for char in ["\n", ".", "!", "?"]:
                # Search within last 100 chars of chunk for natural break
                last_punct = text.rfind(char, start + max_length - 100, end)
                if last_punct != -1 and last_punct > start + overlap:
                    break_point = last_punct + 1
                    break

            chunk = text[start:break_point]
            chunks.append(chunk.strip())
            start = break_point - overlap
        else:
            # We're at the end of text
            chunk = text[start:]
            chunks.append(chunk.strip())
            break

    logger.debug(
        f"Chunked text of length {text_length} into {len(chunks)} chunks "
        f"(max_length={max_length}, overlap={overlap})"
    )
    return chunks
