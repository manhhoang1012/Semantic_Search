import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.pinecone_service import create_index_if_not_exists

create_index_if_not_exists()

print("✅ Index created!")