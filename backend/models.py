"""
models.py — Pydantic request and response schemas.

Keeping models separate from route logic makes validation easy to extend
(e.g. adding conversation history or metadata fields later).
"""

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    """Body sent by the frontend when the user submits a question."""
    question: str = Field(..., min_length=3, max_length=500, description="User question (3 to 500 characters)")
    stream: bool = Field(False, description="Enable real-time token streaming via Server-Sent Events")


class ChunkInfo(BaseModel):
    """Information for a single retrieved chunk."""
    page: int
    content: str


class AnswerResponse(BaseModel):
    """Response returned to the frontend after the RAG chain runs."""
    answer: str
    sources: list[int]  # Page numbers of the retrieved chunks (sorted)
    latency: float | None = None  # Total latency in seconds (rounded to 2 decimals)
    chunks: list[ChunkInfo] = []  # Top retrieved document chunks
    # Telemetry & stats:
    retrieval_sec: float | None = None  # Retrieval latency in seconds (2 decimals)
    llm_sec: float | None = None  # Model answer latency in seconds (2 decimals)
    ttft_sec: float | None = None  # Time to first token in seconds (2 decimals)
    retrieval_ms: float | None = None
    llm_ms: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_cost: float | None = None
    model: str | None = None
