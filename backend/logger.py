"""
logger.py — Terminal logging helpers for RAG request/response inspection.

Keeps all print/log formatting out of the route handlers so they stay clean.
"""


def log_request(question: str) -> None:
    """Print the incoming question with a separator."""
    print(f"\n{'='*80}")
    print(f"📩 QUESTION: {question}")
    print(f"{'='*80}")


def log_chunks(docs: list, elapsed_ms: float) -> None:
    """Print each retrieved chunk: index, page, content preview, and retrieval time."""
    print(f"\n📄 RETRIEVED CHUNKS ({len(docs)}) — ⏱ {elapsed_ms:.0f} ms")
    print(f"{'-'*80}")
    for i, doc in enumerate(docs, start=1):
        page = doc.metadata.get("page", "?")
        preview = doc.page_content[:200].replace("\n", " ")
        if len(doc.page_content) > 200:
            preview += "..."
        print(f"  Chunk {i} | Page {page} | {preview}")
    print(f"{'-'*80}")


def log_answer(answer: str, elapsed_ms: float) -> None:
    """Print the LLM-generated answer and how long it took."""
    print(f"\n🤖 LLM ANSWER — ⏱ {elapsed_ms:.0f} ms:")
    print(f"{'-'*80}")
    print(f"  {answer}")
    print(f"{'='*80}\n")
