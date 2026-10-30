"""
llm.py — LLM instances and RAG chain orchestration.

Uses the OpenAI Responses API with OPENAI_API_KEY.
Optionally override the base URL via OPENAI_BASE_URL (for Azure or proxies).
"""

import os
from pathlib import Path
from openai import OpenAI
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def get_openai_client() -> OpenAI:
    """Returns an OpenAI client. Reads OPENAI_API_KEY and optional OPENAI_BASE_URL."""
    return OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
    )


def get_prompt_text(prompt_file=None) -> str:
    """Loads system instructions from the prompts directory."""
    file_name = prompt_file or os.getenv("RAG_PROMPT_FILE", "v2.txt")
    return (PROMPTS_DIR / file_name).read_text(encoding="utf-8").strip()


def generate_rag_answer(context: str, question: str) -> dict:
    """
    Calls OpenAI Responses API with context and question.
    Returns answer, token metrics, total cost (gpt-4.1-mini pricing), and model name.
    """
    client = get_openai_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    system_instructions = get_prompt_text()
    full_instructions = f"{system_instructions}\n\nContexto:\n{context}"

    response = client.responses.create(
        model=model,
        instructions=full_instructions,
        input=question,
        max_output_tokens=600,
    )

    input_tokens = 0
    output_tokens = 0
    cached_tokens = 0

    if response.usage:
        input_tokens = response.usage.input_tokens or 0
        output_tokens = response.usage.output_tokens or 0
        details = getattr(response.usage, "input_tokens_details", None)
        if details:
            cached_tokens = getattr(details, "cached_tokens", 0) or 0

    # Pricing for gpt-4.1-mini:
    # Input: $0.40 / 1M | Cached input: $0.10 / 1M | Output: $1.60 / 1M
    uncached_input = max(0, input_tokens - cached_tokens)
    total_cost = (
        (uncached_input * 0.40) + (cached_tokens * 0.10) + (output_tokens * 1.60)
    ) / 1_000_000

    return {
        "answer": response.output_text,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_cost": round(total_cost, 6),
        "model": getattr(response, "model", None) or model,
    }


def stream_rag_answer(context: str, question: str):
    """
    Streams OpenAI Responses API output chunks in real time.
    Yields events:
      - {"type": "delta", "delta": str} for each text chunk
      - {"type": "completed", "answer": str, "input_tokens": int, "output_tokens": int, "total_cost": float, "model": str}
    """
    client = get_openai_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    system_instructions = get_prompt_text()
    full_instructions = f"{system_instructions}\n\nContexto:\n{context}"

    stream = client.responses.create(
        model=model,
        instructions=full_instructions,
        input=question,
        max_output_tokens=600,
        stream=True,
    )

    full_answer = []

    for event in stream:
        if event.type == "response.output_text.delta":
            delta = event.delta or ""
            full_answer.append(delta)
            yield {"type": "delta", "delta": delta}
        elif event.type == "response.completed":
            response = event.response
            input_tokens = 0
            output_tokens = 0
            cached_tokens = 0

            if getattr(response, "usage", None):
                input_tokens = response.usage.input_tokens or 0
                output_tokens = response.usage.output_tokens or 0
                details = getattr(response.usage, "input_tokens_details", None)
                if details:
                    cached_tokens = getattr(details, "cached_tokens", 0) or 0

            # Pricing for gpt-4.1-mini:
            # Input: $0.40 / 1M | Cached input: $0.10 / 1M | Output: $1.60 / 1M
            uncached_input = max(0, input_tokens - cached_tokens)
            total_cost = (
                (uncached_input * 0.40) + (cached_tokens * 0.10) + (output_tokens * 1.60)
            ) / 1_000_000

            yield {
                "type": "completed",
                "answer": "".join(full_answer),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_cost": round(total_cost, 6),
                "model": getattr(response, "model", None) or model,
            }


def get_rag_chain(retriever):
    """Builds and returns the RAG chain using the OpenAI Responses API."""
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def generate_answer(inputs: dict) -> str:
        res = generate_rag_answer(inputs["context"], inputs["question"])
        return res["answer"]

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RunnableLambda(generate_answer)
    )
    return chain

