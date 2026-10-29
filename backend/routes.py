"""
routes.py — FastAPI route definitions.

Each endpoint is defined here as an APIRouter, then registered in main.py.
Keeping routes separate from app setup makes it easy to add new routers
(e.g. /history, /documents) without touching main.py.
"""

import re
import time

from fastapi import APIRouter, HTTPException
from models import QuestionRequest, AnswerResponse, ChunkInfo
from state import state
from logger import log_request, log_chunks, log_answer
from rag_pipeline.llm import generate_rag_answer

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check — confirms the server is running and the pipeline is loaded."""
    ready = state.retriever is not None
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
        2. Retrieve the most relevant document chunks (timed).
        3. Log chunks to terminal.
        4. Call OpenAI Responses API with retrieved context (timed).
        5. Return answer with retrieval & model latencies, tokens, cost, and sources.
    """
    if state.retriever is None:
        raise HTTPException(status_code=503, detail="Pipeline not ready yet")

    try:
        # 1. Retrieve relevant chunks and measure retrieval time
        t0 = time.perf_counter()
        source_docs = state.retriever.invoke(req.question)
        retrieval_duration = time.perf_counter() - t0
        retrieval_sec = round(retrieval_duration, 2)
        retrieval_ms = round(retrieval_duration * 1000, 1)
        log_chunks(source_docs, retrieval_ms)

        # 2. Format context & generate answer with OpenAI Responses API
        context = "\n\n".join(doc.page_content for doc in source_docs)
        t1 = time.perf_counter()
        rag_result = generate_rag_answer(context, req.question)
        llm_duration = time.perf_counter() - t1
        llm_sec = round(llm_duration, 2)
        llm_ms = round(llm_duration * 1000, 1)
        log_answer(rag_result["answer"], llm_ms)

        # Measure total end-to-end backend latency in seconds
        total_latency_sec = round(time.perf_counter() - t0, 2)

        # Collect unique source page numbers
        source_pages = sorted(set(
            doc.metadata.get("page", 0) for doc in source_docs
        ))

        # Package top 5 chunks for inspection (sanitizing single line breaks)
        top_chunks = [
            ChunkInfo(
                page=int(doc.metadata.get("page", 0)),
                content=re.sub(r'(?<!\n)\n(?!\n)', ' ', doc.page_content).strip(),
            )
            for doc in source_docs[:5]
        ]

        return AnswerResponse(
            answer=rag_result["answer"],
            sources=source_pages,
            latency=total_latency_sec,
            chunks=top_chunks,
            retrieval_sec=retrieval_sec,
            llm_sec=llm_sec,
            retrieval_ms=retrieval_ms,
            llm_ms=llm_ms,
            input_tokens=rag_result["input_tokens"],
            output_tokens=rag_result["output_tokens"],
            total_cost=rag_result["total_cost"],
            model=rag_result["model"],
        )
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Error en el servidor: {type(e).__name__}: {str(e)}"
        )
