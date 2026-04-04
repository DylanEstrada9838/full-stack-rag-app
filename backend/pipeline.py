"""
pipeline.py — RAG pipeline initialisation and teardown.

Responsible for loading the vectorstore, building the retriever and the
LangChain RAG chain, and storing them in the shared AppState.
Called during FastAPI's lifespan startup event inside main.py.
"""

import sys
from config import RAG_DIR, CHROMA_DB_PATH, RERANKER_TOP_N
from state import state

# Add rag_pipeline to sys.path so its internal imports resolve correctly
sys.path.insert(0, RAG_DIR)

from rag_pipeline.vectorstore import load_vectorstore
from rag_pipeline.chunking import get_chunks
from rag_pipeline.retriever import get_hybrid_retriever, get_reranker_retriever
from rag_pipeline.llm import get_rag_chain


def load_pipeline() -> None:
    """
    Load all RAG components and store them in the shared state.

    Steps:
        1. Load the pre-built Chroma vectorstore from disk.
        2. Rebuild document chunks (needed for BM25 in the hybrid retriever).
        3. Build the hybrid retriever (dense MMR + sparse BM25).
        4. Wrap with a cross-encoder reranker.
        5. Build the full LangChain RAG chain.
    """
    print("🔍 Loading vectorstore...")
    vectorstore = load_vectorstore(persist_dir=CHROMA_DB_PATH)

    print("✂️  Building chunks for BM25...")
    chunks = get_chunks()

    print("🔗 Building hybrid retriever + reranker...")
    hybrid = get_hybrid_retriever(vectorstore, chunks)
    state.retriever = get_reranker_retriever(hybrid, top_n=RERANKER_TOP_N)

    print("🧠 Building RAG chain (retriever → prompt → LLM)...")
    state.chain = get_rag_chain(state.retriever)

    print("✅ RAG pipeline ready!\n")


def unload_pipeline() -> None:
    """Clean up state on shutdown (placeholder for future resource cleanup)."""
    state.retriever = None
    state.chain = None
    print("👋 Pipeline unloaded.")
