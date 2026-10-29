import os
import pickle
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever

from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_classic.retrievers import ContextualCompressionRetriever


def create_bm25_retriever(chunks, k=5, k1=1.2, b=0.75):
    """Creates a BM25Retriever from document chunks."""
    return BM25Retriever.from_documents(
        documents=chunks,
        k=k,
        k1=k1,
        b=b,
    )


def save_bm25_retriever(bm25_retriever, filepath):
    """Saves the BM25Retriever instance to disk using pickle."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, "wb") as f:
        pickle.dump(bm25_retriever, f)
    print(f"[BM25] Index cached to: {filepath}")


def load_bm25_retriever(filepath=None, chunks=None):
    """
    Loads pre-computed BM25Retriever from disk.
    If not found on disk, computes it from chunks and caches it.
    """
    if filepath and os.path.exists(filepath):
        try:
            with open(filepath, "rb") as f:
                retriever = pickle.load(f)
            print(f"[BM25] Loaded pre-built index from disk: {filepath}")
            return retriever
        except Exception as e:
            print(f"[BM25] Failed to load cached index ({e}). Rebuilding...")

    if chunks is None:
        from rag_pipeline.chunking import get_chunks
        chunks = get_chunks()

    retriever = create_bm25_retriever(chunks)
    if filepath:
        save_bm25_retriever(retriever, filepath)
    return retriever


def get_hybrid_retriever(vectorstore, chunks=None, bm25_retriever=None, bm25_path=None):
    """
    Builds the hybrid EnsembleRetriever (dense MMR ChromaDB + sparse BM25).
    Loads pre-built BM25 index if available to eliminate startup latency.
    """
    vec_retriever = vectorstore.as_retriever(
        search_kwargs={"k": 5}, 
        search_type="mmr",
        fetch_k=20,
        lambda_mult=0.3,
    )

    if bm25_retriever is None:
        bm25_retriever = load_bm25_retriever(filepath=bm25_path, chunks=chunks)

    return EnsembleRetriever(
        retrievers=[vec_retriever, bm25_retriever],
        weights=[0.6, 0.4],
    )

def get_reranker_retriever(base_retriever, top_n=5):
    """
    Wraps an existing retriever with a Cross-Encoder reranker.
    Uses a multilingual model since documents and queries are in Spanish.
    """
    model = HuggingFaceCrossEncoder(
        # BAAI/bge-reranker-v2-m3 is excellent for multilingual queries
        model_name="BAAI/bge-reranker-v2-m3",
        model_kwargs={"device": "cpu"}
    )
    compressor = CrossEncoderReranker(model=model, top_n=top_n)
    
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor, 
        base_retriever=base_retriever
    )
    return compression_retriever
