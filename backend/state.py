"""
state.py — Shared application state container.

Holds the heavy ML objects (retriever, chain) that are loaded once on startup
and reused across every request. Imported by both pipeline.py and routes.py.
"""


class AppState:
    """
    Singleton-style container for the loaded RAG pipeline objects.

    Attributes:
        retriever: The retriever (hybrid + reranker) used to fetch chunks.
        chain:     The full LangChain RAG chain (retriever → prompt → LLM → text).
    """
    retriever = None
    chain = None


# Single shared instance — imported wherever needed
state = AppState()
