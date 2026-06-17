from .embedding_service import EmbeddingService
from .chroma_store import ChromaStore
from .bm25_store import BM25Store


class EmbeddingGenerator:
    """
    Embedding management layer.

    Responsible for:
    - Generating embeddings
    - Storing embeddings in ChromaDB
    - Storing chunks in BM25
    - Query embedding generation
    - Vector similarity search
    """

    def __init__(self, config):

        # Embedding model service
        self.embedding_service = EmbeddingService(config)

        # Dense vector store
        self.chroma_store = ChromaStore(config, self.embedding_service)

        # Sparse retrieval store
        self.bm25_store = BM25Store(config)


    def process(self, document):
        """
        Index a document in all retrieval backends.

        Stores:
        - Dense embeddings in ChromaDB
        - Sparse representations in BM25
        """

        self.chroma_store.add_document(document)

        self.bm25_store.add_document(document)


    def get_query_embedding(self, query):
        """
        Generate an embedding for a user query.
        """

        return self.embedding_service.encode([query])[0]


    def search(self, query, top_k=5):
        """
        Perform dense vector retrieval using
        ChromaDB.
        """

        query_embedding = self.get_query_embedding(query)

        return self.chroma_store.search(
            query_embedding,
            top_k
        )