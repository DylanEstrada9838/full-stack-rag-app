"""
llm.py — LLM instances and RAG chain orchestration.

Provides utility functions to instantiate the Groq language model
and build the LangChain prompt and LCEL chain for retrieval-augmented generation.
"""

import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser


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


def get_prompt():
    """Returns the ChatPromptTemplate for the RAG chain."""
    return ChatPromptTemplate.from_messages([
        ("system",
          """
Eres un asistente experto en el Reglamento General de Estudiantes 
del Tecnológico de Monterrey.

Tu tarea es responder únicamente con la información proporcionada 
en el contexto recuperado.

Instrucciones importantes:
- Indica el artículo específico del reglamento del cual proviene la respuesta.
- Si es posible, menciona también el capítulo, sección o título relacionado.
- Si múltiples artículos aplican, enuméralos claramente.
- No inventes artículos, números o información que no aparezcan en el contexto.
- Si la respuesta no se encuentra en el contexto, responde:
  "No tengo suficiente información en el contexto proporcionado."
"""
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
