"""
config.py — Configuration constants for the backend.

Centralizes all paths and settings so they are easy to change in one place.
"""

import os

# Absolute path to the rag_pipeline package directory
RAG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rag_pipeline")

# Path to the pre-built Chroma vectorstore
CHROMA_DB_PATH = os.path.join(RAG_DIR, "chroma_db")

# Reranker top-n results to keep
RERANKER_TOP_N = 5

# Origins allowed to call the API.
# - localhost:5173 → Vite dev server
# - localhost:80 / localhost → Docker nginx
# - EXTRA_CORS_ORIGINS → comma-separated list for production deployments
_extra = os.getenv("EXTRA_CORS_ORIGINS", "")
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost",
    "http://localhost:80",
    "http://127.0.0.1",
    "http://127.0.0.1:80",
    *[o.strip() for o in _extra.split(",") if o.strip()],
]
