"""
config.py — Configuration constants for the backend.

Centralizes all paths and settings so they are easy to change in one place.
"""

import os

# Absolute path to the rag_pipeline package directory
RAG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rag_pipeline")

# Path to the pre-built Chroma vectorstore
CHROMA_DB_PATH = os.path.join(RAG_DIR, "chroma_db")

# Path to the pre-built BM25 retriever index
BM25_INDEX_PATH = os.path.join(RAG_DIR, "bm25_retriever.pkl")

# Reranker top-n results to keep
RERANKER_TOP_N = 5

# Origins allowed to call the API.
# Defaults to ["*"] so that Vercel, production domains, and local dev work without CORS blocks.
_extra = os.getenv("EXTRA_CORS_ORIGINS", "*")
CORS_ORIGINS = [
    "*",
    *[o.strip().rstrip('/') for o in _extra.split(",") if o.strip()],
]
