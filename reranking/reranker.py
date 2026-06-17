from sentence_transformers import CrossEncoder


class Reranker:

    def __init__(self, config):

        self.model = CrossEncoder(config["reranker_model_path"])


    def rerank(self, query, chunks, top_k=7):

        if not chunks:
            return []
    
        rerankable_chunks = [chunk for chunk in chunks if chunk["chunk_type"] != "figure"]
        figure_chunks = [chunk for chunk in chunks if chunk["chunk_type"] == "figure"]

        pairs = [
            (query, rerankable_chunk["content"])
            for rerankable_chunk in rerankable_chunks
        ]

        scores = self.model.predict(pairs)

        for rerankable_chunk, score in zip(rerankable_chunks, scores):
            rerankable_chunk["rerank_score"] = float(score)

        rerankable_chunks.sort(
            key=lambda x: x["rerank_score"],
            reverse=True
        )

        final_chunks = rerankable_chunks[:top_k] + figure_chunks

        return final_chunks