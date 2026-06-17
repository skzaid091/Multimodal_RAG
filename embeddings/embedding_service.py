from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Wrapper around the SentenceTransformer model.

    Responsible for:
    - Loading the embedding model
    - Generating normalized embeddings
    """

    def __init__(self, config):

        # Load embedding model
        self.model = SentenceTransformer(
            config["embedding_model_path"]
        )

    def encode(self, texts):
        """
        Generate embeddings for the provided texts.

        Args:
            texts (list[str]):
                Input texts to embed.

        Returns:
            numpy.ndarray:
                Normalized embeddings.
        """

        return self.model.encode(
            texts,

            # Normalize embeddings for
            # cosine similarity search
            normalize_embeddings=True
        )