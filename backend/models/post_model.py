"""
Post model representing a document/chunk in the vector database
"""

from typing import Optional
from dataclasses import dataclass, asdict


@dataclass
class Post:
    """
    Represents a document chunk stored in Pinecone.

    Attributes:
        id: Unique identifier for this chunk
        title: Document title
        content: Chunk content
        subreddit: Original subreddit (if from Reddit)
        score: Post score/karma
        comments: Number of comments
        username: Author username
        parent_id: ID of the parent document (for grouping chunks)
        chunk_index: Index of this chunk within the document
        category: Document category
        author: Author name
    """

    id: str
    title: str
    content: str
    subreddit: Optional[str] = None
    score: int = 0
    comments: int = 0
    username: Optional[str] = None
    parent_id: Optional[str] = None
    chunk_index: int = 0
    category: Optional[str] = None
    author: Optional[str] = None

    def __post_init__(self):
        """Ensure parent_id defaults to id"""
        if self.parent_id is None:
            self.parent_id = self.id

    def to_dict(self) -> dict:
        """Convert to dictionary for metadata storage"""
        return asdict(self)