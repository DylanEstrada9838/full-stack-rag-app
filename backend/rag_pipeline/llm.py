"""
llm.py — LLM instances and RAG chain orchestration.

Provides utility functions to instantiate the Groq language model
and build the LangChain prompt and LCEL chain for retrieval-augmented generation.
"""

import os
from pathlib import Path
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def get_llm(model=None, temperature=0.3):
    """
    Return a Groq LLM instance.

    Requires the GROQ_API_KEY environment variable to be set.
    Optionally override the model via the GROQ_MODEL env variable.
    """
    groq_model = model or os.getenv("GROQ_MODEL") or "openai/gpt-oss-120b"
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise ValueError(
            "GROQ_API_KEY env variable is required. "
            "Get a free key at https://console.groq.com"
        )
    print(f"🤖 Using Groq LLM  →  model={groq_model}")
    return ChatGroq(
        model=groq_model,
        temperature=temperature,
        api_key=groq_key,
    )


def get_prompt(prompt_file=None):
    """Returns the ChatPromptTemplate for the RAG chain loading from prompts/."""
    file_name = prompt_file or os.getenv("RAG_PROMPT_FILE", "v2.txt")
    prompt_path = PROMPTS_DIR / file_name
    system_text = prompt_path.read_text(encoding="utf-8").strip()

    return ChatPromptTemplate.from_messages([
        ("system", f"{system_text}\n\nContexto:\n{{context}}"),
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
