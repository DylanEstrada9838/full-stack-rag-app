import os
import shutil
from dotenv import load_dotenv
from langchain_chroma import Chroma
from rag_pipeline.chunking import get_chunks
from rag_pipeline.embeddings import get_embeddings


def create_vector_db(chunking_config=None, persist_dir=None):
    """
    Create a new Chroma vector store.

    Args:
        chunking_config: dict passed to get_chunks() to control chunking.
        persist_dir:     explicit directory path. If None, defaults to chroma_db.

    Returns:
        (vectorstore, persist_dir, chunks)
    """
    chunks = get_chunks(chunking_config)
    embeddings = get_embeddings()

    if persist_dir is None:
        persist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")

    # Always start fresh
    if os.path.exists(persist_dir):
        for item in os.listdir(persist_dir):
            item_path = os.path.join(persist_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    return vectorstore, persist_dir, chunks


def load_vectorstore(persist_dir=None):
    if persist_dir is None:
        persist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chroma_db")
    return Chroma(persist_directory=persist_dir, embedding_function=get_embeddings())