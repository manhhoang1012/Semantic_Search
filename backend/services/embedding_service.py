from sentence_transformers import SentenceTransformer
from backend.config import MODEL_NAME

model = SentenceTransformer(MODEL_NAME)

def embed_text(text: str):
    return model.encode(text).tolist()