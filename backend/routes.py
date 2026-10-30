"""
routes.py — FastAPI route definitions.

Each endpoint is defined here as an APIRouter, then registered in main.py.
Keeping routes separate from app setup makes it easy to add new routers
(e.g. /history, /documents) without touching main.py.
"""

import json
import re
import time

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from models import QuestionRequest, AnswerResponse, ChunkInfo
from state import state
from logger import log_request, log_chunks, log_answer
from rag_pipeline.llm import generate_rag_answer, stream_rag_answer

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check — confirms the server is running and the pipeline is loaded."""
    ready = state.retriever is not None
    return {
        "status": "ok" if ready else "loading",
        "pipeline_ready": ready,
    }


def stream_generator(question: str):
    """
    Generator that yields Server-Sent Events (SSE) for streaming RAG responses.
    Events:
      1. {"type": "retrieval", "retrieval_sec": float, "sources": list[int], "chunks": list[dict]}
      2. {"type": "delta", "delta": str} (repeated for each token)
      3. {"type": "done", "answer": str, "latency": float, "retrieval_sec": float, "llm_sec": float, ...}
    """
    try:
        log_request(question)

        # 1. Retrieve chunks and measure time
        t0 = time.perf_counter()
        source_docs = state.retriever.invoke(question)
        retrieval_duration = time.perf_counter() - t0
        retrieval_sec = round(retrieval_duration, 2)
        retrieval_ms = round(retrieval_duration * 1000, 1)
        log_chunks(source_docs, retrieval_ms)

        source_pages = sorted(set(
            doc.metadata.get("page", 0) for doc in source_docs
        ))

        top_chunks = [
            {
                "page": int(doc.metadata.get("page", 0)),
                "content": re.sub(r'(?<!\n)\n(?!\n)', ' ', doc.page_content).strip(),
            }
            for doc in source_docs[:5]
        ]

        # Send initial metadata with retrieved chunks
        init_event = {
            "type": "retrieval",
            "retrieval_sec": retrieval_sec,
            "sources": source_pages,
            "chunks": top_chunks,
        }
        yield f"data: {json.dumps(init_event, ensure_ascii=False)}\n\n"

        # 2. Stream generation with OpenAI Responses API
        context = "\n\n".join(doc.page_content for doc in source_docs)
        t1 = time.perf_counter()
        first_token_time = None

        for chunk_data in stream_rag_answer(context, question):
            if chunk_data["type"] == "delta":
                if first_token_time is None and chunk_data.get("delta"):
                    first_token_time = time.perf_counter()
                payload = {"type": "delta", "delta": chunk_data["delta"]}
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            elif chunk_data["type"] == "completed":
                llm_duration = time.perf_counter() - t1
                llm_sec = round(llm_duration, 2)
                total_latency_sec = round(time.perf_counter() - t0, 2)
                ttft_sec = round(first_token_time - t0, 2) if first_token_time else None
                log_answer(chunk_data["answer"], llm_duration * 1000)

                completed_payload = {
                    "type": "done",
                    "answer": chunk_data["answer"],
                    "latency": total_latency_sec,
                    "retrieval_sec": retrieval_sec,
                    "llm_sec": llm_sec,
                    "ttft_sec": ttft_sec,
                    "input_tokens": chunk_data["input_tokens"],
                    "output_tokens": chunk_data["output_tokens"],
                    "total_cost": chunk_data["total_cost"],
                    "model": chunk_data["model"],
                }
                yield f"data: {json.dumps(completed_payload, ensure_ascii=False)}\n\n"

    except Exception as e:
        import traceback
        traceback.print_exc()
        err_payload = {"type": "error", "error": f"{type(e).__name__}: {str(e)}"}
        yield f"data: {json.dumps(err_payload, ensure_ascii=False)}\n\n"


@router.post("/ask")
def ask_question(req: QuestionRequest):
    """
    Main Q&A endpoint. Supports both streaming (SSE) and standard JSON response.
    """
    if state.retriever is None:
        raise HTTPException(status_code=503, detail="Pipeline not ready yet")

    if req.stream:
        return StreamingResponse(
            stream_generator(req.question),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

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
