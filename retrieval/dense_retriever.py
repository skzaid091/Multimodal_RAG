class DenseRetriever:

    def __init__(self, chroma_store):

        self.chroma_store = chroma_store


    def retrieve(self, query, top_k=10):

        results = self.chroma_store.query(query, top_k)

        retrieved = []

        ids = results["ids"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]

        for chunk_id, score, metadata in zip(ids, distances, metadatas):

            retrieved.append(
                {
                    "document_id": metadata["document_id"],
                    "chunk_index": metadata["chunk_index"],
                    "chunk_type": metadata["chunk_type"],
                    "chunk_id": chunk_id,
                    "score": score,
                }
            )

        return retrieved