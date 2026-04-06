import pandas as pd

df = pd.read_csv("data/raw/reddit_posts.csv", encoding="latin-1")

# chọn cột cần thiết
df = df[[
    "reddit_id",
    "title",
    "subreddit",
    "score",
    "number_of_comments",
    "username"
]]

# xóa null
df = df.dropna()

# lưu lại
df.to_csv("data/processed/clean_data.csv", index=False)

print("✅ Preprocess done!")