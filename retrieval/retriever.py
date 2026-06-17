from embeddings.embedding_service import EmbeddingService
from embeddings.chroma_store import ChromaStore
from embeddings.bm25_store import BM25Store

from .dense_retriever import DenseRetriever
from .bm25_retriever import BM25Retriever
from .hybrid_retriever import HybridRetriever

from .chunk_retriever import ChunkRetriever
from .neighborhood_retriever import NeighborhoodRetriever


class Retriever:

    def __init__(self, config):

        self.config = config

        embedding_service = EmbeddingService(config)
        chroma_store = ChromaStore(config, embedding_service)
        bm25_store = BM25Store(config)

        self.dense_retriever = DenseRetriever(chroma_store)
        self.bm25_retriever = BM25Retriever(bm25_store)

        self.hybrid_retriever = HybridRetriever(
            self.dense_retriever,
            self.bm25_retriever
        )

        chunk_retriever = ChunkRetriever(config)
        self.neighborhood_retriever = NeighborhoodRetriever(chunk_retriever)


    def retrieve(self, query, top_k=10):

        retrieval_type = self.config["retrieval_type"]

        if retrieval_type == "dense":
            chunks = self.dense_retriever.retrieve(
                query=query,
                top_k=top_k
            )

        elif retrieval_type == "bm25":
            chunks = self.bm25_retriever.retrieve(
                query=query,
                top_k=top_k
            )

        elif retrieval_type == "hybrid":
            chunks = self.hybrid_retriever.retrieve(
                query=query,
                top_k=top_k
            )

        else:
            raise ValueError(
                f"Unknown retrieval type: {retrieval_type}"
            )

        chunks.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        chunks = self.neighborhood_retriever.retrieve(chunks)
        
        
        return chunks