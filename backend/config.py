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

# Origins allowed to call the API (React dev server)
CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
