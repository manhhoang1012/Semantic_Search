class Post:
    def __init__(self, id, title, subreddit, score, comments, username):
        self.id = id
        self.title = title
        self.subreddit = subreddit
        self.score = score
        self.comments = comments
        self.username = username

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "subreddit": self.subreddit,
            "score": self.score,
            "comments": self.comments,
            "username": self.username
        }