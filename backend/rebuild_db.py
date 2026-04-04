import os
import sys
from config import CHROMA_DB_PATH, RAG_DIR

# Add rag_pipeline to sys.path so its internal imports resolve correctly
sys.path.insert(0, RAG_DIR)

from rag_pipeline.vectorstore import create_vector_db

def rebuild():
    print(f"🚀 Initializing Vector Database at: {CHROMA_DB_PATH}")
    
    # If the directory exists, it will be wiped and recreated by create_vector_db
    vectorstore, persist_dir, chunks = create_vector_db(persist_dir=CHROMA_DB_PATH)
    
    print(f"✅ Success! Database created with {len(chunks)} chunks.")
    print(f"📍 Location: {persist_dir}")

if __name__ == "__main__":
    rebuild()
