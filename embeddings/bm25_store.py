import json
import os

from rank_bm25 import BM25Okapi


class BM25Store:
    """
    BM25-based sparse retrieval store.

    Responsible for:
    - Storing chunk metadata
    - Building BM25 indexes
    - Executing sparse retrieval
    - Persisting indexes to disk
    """

    def __init__(self, config):

        self.config = config

        # BM25 index storage path
        self.index_path = config["bm25_index_path"]

        # Stored chunk records
        self.records = []

        # In-memory BM25 index
        self.bm25 = None

        # Load existing index if available
        if os.path.exists(self.index_path):
            self.load()


    def add_document(self, document):
        """
        Add a document to the BM25 index.

        Existing chunks belonging to the same document
        are removed before re-indexing.
        """

        # Remove old version if document already exists
        self.records = [
            record
            for record in self.records
            if record["document_id"] != document.document_id
        ]

        # Add all document chunks
        for chunk in document.chunks:

            self.records.append(
                {
                    "document_id": chunk.document_id,
                    "chunk_id": chunk.chunk_id,
                    "chunk_index": chunk.chunk_index,
                    "content": chunk.content,
                }
            )

        # Rebuild BM25 index
        self._rebuild()

        # Persist changes
        self.save()


    def _rebuild(self):
        """
        Rebuild the in-memory BM25 index
        from the current records.
        """

        if not self.records:
            self.bm25 = None
            return

        corpus = [
            record["content"].split()
            for record in self.records
        ]

        self.bm25 = BM25Okapi(corpus)


    def search(self, query, top_k=10):
        """
        Perform BM25 retrieval.

        Returns:
            List of matching chunks sorted by score.
        """

        if self.bm25 is None:
            return []

        scores = self.bm25.get_scores(
            query.split()
        )

        results = []

        for record, score in zip(self.records, scores):

            results.append(
                {
                    "document_id": record["document_id"],
                    "chunk_id": record["chunk_id"],
                    "chunk_index": record["chunk_index"],
                    "score": float(score)
                }
            )

        # Sort by relevance score
        results.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        return results[:top_k]


    def save(self):
        """
        Persist BM25 records to disk.

        Only records are stored.
        The BM25 index is rebuilt during loading.
        """

        os.makedirs(
            os.path.dirname(self.index_path),
            exist_ok=True
        )

        with open(self.index_path, "w", encoding="utf-8") as file:

            json.dump(
                {
                    "records": self.records
                },
                file,
                ensure_ascii=False,
                indent=4
            )


    def load(self):
        """
        Load BM25 records from disk and
        rebuild the BM25 index.
        """

        with open(self.index_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        self.records = data.get("records", [])

        self._rebuild()


    def delete_document(self, document_id):
        """
        Remove all chunks belonging to
        the specified document.
        """

        self.records = [
            record
            for record in self.records
            if record["document_id"] != document_id
        ]

        # Rebuild BM25 index after deletion
        self._rebuild()

        # Persist updated index
        self.save()