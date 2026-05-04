import sys
import os
sys.path.append("d:\\Pinecone")

from backend.services.pinecone_service import get_index

try:
    index = get_index()
    res = index.list(limit=5)
    print("List output:")
    for page in res:
        print(page)
except Exception as e:
    print("Error:", e)
