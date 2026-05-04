class Post:
    def __init__(self, id, title, content, subreddit, score, comments, username, parent_id=None, chunk_index=None):
        self.id = id
        self.title = title
        self.content = content
        self.subreddit = subreddit
        self.score = score
        self.comments = comments
        self.username = username
        self.parent_id = parent_id or id
        self.chunk_index = chunk_index or 0

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "subreddit": self.subreddit,
            "score": self.score,
            "comments": self.comments,
            "username": self.username,
            "parent_id": self.parent_id,
            "chunk_index": self.chunk_index
        }