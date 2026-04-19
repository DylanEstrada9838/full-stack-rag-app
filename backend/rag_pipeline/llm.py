"""
llm.py — LLM instances and RAG chain orchestration.

Provides utility functions to instantiate language models (Groq or Ollama)
and build the LangChain prompt and LCEL chain for retrieval-augmented generation.
"""

import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


def get_llm(model=None, temperature=0.3):
    """
    Return an LLM instance based on the LLM_PROVIDER env variable.

    Supported providers:
        - "groq"   → Uses Groq cloud API (requires GROQ_API_KEY).
        - "ollama"  → Uses a local / Docker Ollama server (default).
    """
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    if provider == "groq":
        # Default Groq model — fast & free-tier friendly
        groq_model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
        groq_key = os.getenv("GROQ_API_KEY")
        if not groq_key:
            raise ValueError(
                "GROQ_API_KEY env variable is required when LLM_PROVIDER=groq"
            )
        print(f"🤖 Using Groq LLM  →  model={groq_model}")
        return ChatGroq(
            model=groq_model,
            temperature=temperature,
            api_key=groq_key,
        )

    # ── Default: Ollama ──────────────────────────────────────────────
    ollama_model = model or "llama3"
    # OLLAMA_HOST is set to http://ollama:11434 in Docker,
    # falls back to localhost for local development.
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    print(f"🤖 Using Ollama LLM →  model={ollama_model}")
    return ChatOllama(
        model=ollama_model,
        temperature=temperature,
        base_url=ollama_host,
    )


def get_prompt():
    """Returns the ChatPromptTemplate for the RAG chain."""
    return ChatPromptTemplate.from_messages([
        ("system",
         "Eres un asistente experto en el Reglamento General de Estudiantes "
         "del Tecnológico de Monterrey. Responde únicamente con la información "
         "proporcionada en el contexto. Si la respuesta no se encuentra en el "
         "contexto, indica que no tienes suficiente información.\n\n"
         "Contexto:\n{context}"),
        ("human", "{question}"),
    ])


def get_rag_chain(retriever):
    """Builds and returns the full LCEL RAG chain."""
    llm = get_llm()
    prompt = get_prompt()

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain
