"""
routes.py — FastAPI route definitions.

Each endpoint is defined here as an APIRouter, then registered in main.py.
Keeping routes separate from app setup makes it easy to add new routers
(e.g. /history, /documents) without touching main.py.
"""

import time

from fastapi import APIRouter
from models import QuestionRequest, AnswerResponse
from state import state
from logger import log_request, log_chunks, log_answer

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check — confirms the server is running and the pipeline is loaded."""
    ready = state.chain is not None
    return {
        "status": "ok" if ready else "loading",
        "pipeline_ready": ready,
    }


@router.post("/ask", response_model=AnswerResponse)
def ask_question(req: QuestionRequest):
    """
    Main Q&A endpoint.

    Flow:
        1. Log the incoming question.
        2. Retrieve the most relevant document chunks.
        3. Log the chunks to the terminal for inspection.
        4. Run the full RAG chain to generate an answer.
        5. Log the answer and return it with source page numbers.
    """
    log_request(req.question)

    # Retrieve relevant chunks and measure time
    t0 = time.perf_counter()
    source_docs = state.retriever.invoke(req.question)
    retrieval_ms = (time.perf_counter() - t0) * 1000
    log_chunks(source_docs, retrieval_ms)

    # Generate the answer and measure time
    t1 = time.perf_counter()
    answer = state.chain.invoke(req.question)
    llm_ms = (time.perf_counter() - t1) * 1000
    log_answer(answer, llm_ms)

    # Collect unique source page numbers
    source_pages = sorted(set(
        doc.metadata.get("page", 0) for doc in source_docs
    ))

    return AnswerResponse(answer=answer, sources=source_pages)
