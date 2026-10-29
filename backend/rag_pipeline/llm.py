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


def get_rag_chain(retriever):
    """Builds and returns the RAG chain using the OpenAI Responses API."""
    client = get_openai_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    system_instructions = get_prompt_text()

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    def generate_answer(inputs: dict) -> str:
        context = inputs["context"]
        question = inputs["question"]
        full_instructions = f"{system_instructions}\n\nContexto:\n{context}"
        response = client.responses.create(
            model=model,
            instructions=full_instructions,
            input=question,
            max_output_tokens=600,
        )
        return response.output_text

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | RunnableLambda(generate_answer)
    )
    return chain

