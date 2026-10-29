
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings


def get_embeddings():
    """
    Returns high-performance ONNX-backed embeddings using FastEmbed.
    Eliminates PyTorch startup overhead and significantly reduces RAM.
    """
    return FastEmbedEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
    )