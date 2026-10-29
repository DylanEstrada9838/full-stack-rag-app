"""
pipeline.py — RAG pipeline initialisation and teardown.

Responsible for loading the vectorstore, building the retriever and the
LangChain RAG chain, and storing them in the shared AppState.
Called during FastAPI's lifespan startup event inside main.py.
"""

import sys
from config import RAG_DIR, CHROMA_DB_PATH, BM25_INDEX_PATH, RERANKER_TOP_N
from state import state

from rag_pipeline.vectorstore import load_vectorstore
from rag_pipeline.retriever import get_hybrid_retriever, get_reranker_retriever
from rag_pipeline.llm import get_rag_chain


def load_pipeline() -> None:
    """
    Load all RAG components and store them in the shared state.

    Steps:
        1. Load the pre-built Chroma vectorstore from disk.
        2. Load the pre-built BM25 index from disk (no chunking on startup).
        3. Build the hybrid retriever (dense MMR + sparse BM25).
        4. Wrap with a cross-encoder reranker (optional).
        5. Build the full LangChain RAG chain.
    """
    print("🔍 Loading vectorstore...")
    vectorstore = load_vectorstore(persist_dir=CHROMA_DB_PATH)

    print("🔗 Loading hybrid retriever (ChromaDB + BM25 cache)...")
    hybrid = get_hybrid_retriever(vectorstore, bm25_path=BM25_INDEX_PATH)
    #state.retriever = get_reranker_retriever(hybrid, top_n=RERANKER_TOP_N)
    state.retriever = hybrid
    print("🧠 Building RAG chain (retriever → prompt → LLM)...")
    state.chain = get_rag_chain(state.retriever)

    print("✅ RAG pipeline ready!\n")


def unload_pipeline() -> None:
    """Clean up state on shutdown (placeholder for future resource cleanup)."""
    state.retriever = None
    state.chain = None
    print("👋 Pipeline unloaded.")
