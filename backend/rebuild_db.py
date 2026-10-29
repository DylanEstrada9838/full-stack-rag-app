import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from config import CHROMA_DB_PATH, BM25_INDEX_PATH, RAG_DIR

from rag_pipeline.vectorstore import create_vector_db
from rag_pipeline.retriever import create_bm25_retriever, save_bm25_retriever

def rebuild(force_vector_db=False):
    # Only recreate vectorstore if requested or if not already created
    if force_vector_db or not os.path.exists(CHROMA_DB_PATH) or not os.listdir(CHROMA_DB_PATH):
        print(f"🚀 Initializing Vector Database at: {CHROMA_DB_PATH}")
        vectorstore, persist_dir, chunks = create_vector_db(persist_dir=CHROMA_DB_PATH)
        print(f"✅ Success! Database created with {len(chunks)} chunks.")
        print(f"📍 Location: {persist_dir}")
    else:
        print(f"📦 Chroma database already exists at: {CHROMA_DB_PATH}")
        from rag_pipeline.chunking import get_chunks
        chunks = get_chunks()

    print(f"🚀 Building and caching BM25 index at: {BM25_INDEX_PATH}")
    bm25 = create_bm25_retriever(chunks)
    save_bm25_retriever(bm25, BM25_INDEX_PATH)
    print("✅ BM25 index successfully pre-built and cached.")

if __name__ == "__main__":
    rebuild()
