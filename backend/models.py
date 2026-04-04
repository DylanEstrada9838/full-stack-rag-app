"""
models.py — Pydantic request and response schemas.

Keeping models separate from route logic makes validation easy to extend
(e.g. adding conversation history or metadata fields later).
"""

from pydantic import BaseModel


class QuestionRequest(BaseModel):
    """Body sent by the frontend when the user submits a question."""
    question: str


class AnswerResponse(BaseModel):
    """Response returned to the frontend after the RAG chain runs."""
    answer: str
    sources: list[int]  # Page numbers of the retrieved chunks (sorted)
