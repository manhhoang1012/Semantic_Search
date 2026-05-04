from sentence_transformers import SentenceTransformer
from backend.config import MODEL_NAME
import threading
from concurrent.futures import ThreadPoolExecutor

class EmbeddingModelSingleton:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EmbeddingModelSingleton, cls).__new__(cls)
                cls._instance._model = None
                cls._instance._executor = ThreadPoolExecutor(max_workers=1)
        return cls._instance

    def get_model(self):
        if self._model is None:
            self._model = SentenceTransformer(MODEL_NAME)
        return self._model
    
    def encode(self, text: str):
        def _encode():
            model = self.get_model()
            return model.encode(text).tolist()
        
        future = self._executor.submit(_encode)
        return future.result()

def embed_text(text: str):
    singleton = EmbeddingModelSingleton()
    return singleton.encode(text)