class HybridRetriever:

    def __init__(self, dense_retriever, bm25_retriever, rrf_k=60):

        self.dense_retriever = dense_retriever
        self.bm25_retriever = bm25_retriever

        self.rrf_k = rrf_k


    def retrieve(self, query, top_k=10):

        dense_results = (
            self.dense_retriever.retrieve(
                query=query,
                top_k=top_k
            )
        )

        bm25_results = (
            self.bm25_retriever.retrieve(
                query=query,
                top_k=top_k
            )
        )

        fused_scores = {}

        self._apply_rrf(dense_results, fused_scores)

        self._apply_rrf(bm25_results, fused_scores)

        results = [
            {
                "document_id": doc_chunk_id_and_index[0],
                "chunk_id": doc_chunk_id_and_index[1],
                "chunk_index": doc_chunk_id_and_index[2],
                "score": score
            }
            for doc_chunk_id_and_index, score
            in fused_scores.items()
        ]

        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:top_k]


    def _apply_rrf(self, results, fused_scores):

        for rank, result in enumerate(results, start=1):
            
            document_id = result["document_id"]
            chunk_id = result["chunk_id"]
            chunk_index = result["chunk_index"]

            score = 1 / (self.rrf_k + rank)

            fused_scores[(document_id, chunk_id, chunk_index)] = fused_scores.get(chunk_id, 0.0) + score