import chromadb


class ChromaStore:
    """
    ChromaDB vector store.

    Responsible for:
    - Storing chunk embeddings
    - Semantic vector retrieval
    - Document-level deletion
    - Managing Chroma collections
    """

    def __init__(self, config, embedding_service=None):

        # Embedding generation service
        self.embedding_service = embedding_service

        # Persistent ChromaDB client
        self.client = chromadb.PersistentClient(
            path=config["chroma_db_path"]
        )

        # Collection used for document storage
        self.collection = (
            self.client.get_or_create_collection(
                name=config["collection_name"]
            )
        )


    def add_document(self, document):
        """
        Add all document chunks to ChromaDB.

        Existing chunks belonging to the same document
        are removed before insertion.
        """

        if not document.chunks:
            return

        # Extract chunk text
        texts = [chunk.content for chunk in document.chunks]

        # Generate embeddings
        embeddings = self.embedding_service.encode(texts)

        self.collection.add(

            ids=[
                chunk.chunk_id
                for chunk in document.chunks
            ],

            embeddings=embeddings.tolist(),

            documents=texts,

            metadatas=[
                {
                    "document_id":
                        str(chunk.document_id),

                    "chunk_id":
                        str(chunk.chunk_id),

                    "chunk_type":
                        str(chunk.chunk_type),

                    "chunk_index":
                        int(chunk.chunk_index),

                    "page_number":
                        str(chunk.page_number),

                    "section_title":
                        (
                            str(chunk.section_title)
                            if chunk.section_title
                            is not None
                            else ""
                        )
                }
                for chunk in document.chunks
            ]
        )


    def search(self, query_embedding, top_k=5):
        """
        Perform vector similarity search using
        a precomputed query embedding.
        """

        return self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=top_k
        )


    def delete_document(self, document_id):
        """
        Remove all chunks belonging to
        the specified document.
        """

        self.collection.delete(
            where={
                "document_id": document_id
            }
        )


    def query(self, query, top_k=10):
        """
        Generate query embedding and perform
        semantic retrieval.
        """

        query_embedding = self.embedding_service.encode([query])[0]

        return self.collection.query(
            query_embeddings=[
                query_embedding.tolist()
            ],
            n_results=top_k
        )