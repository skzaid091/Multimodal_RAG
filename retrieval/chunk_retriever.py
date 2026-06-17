import os
import json

class ChunkRetriever:

    def __init__(self, config):

        self.chunk_storage_path = config["chunk_storage_path"]

        self.cache = {}
    

    def _load_document(self, document_id):

        if document_id in self.cache:
            return self.cache[document_id]

        file_path = os.path.join(self.chunk_storage_path, f"{document_id}.json")

        with open(file_path, "r", encoding="utf-8") as file:
            chunks = json.load(file)

        self.cache[document_id] = chunks

        return chunks


    def get_chunk(self, document_id, chunk_id):

        chunks = self._load_document(document_id)

        for chunk in chunks:

            if chunk["chunk_id"] == chunk_id:
                return chunk

        return None
    

    def get_chunks(self, retrieval_results):

        chunks = []

        for result in retrieval_results:

            chunk = self.get_chunk(result["document_id"], result["chunk_id"])

            if chunk:
                chunks.append(chunk)

        return chunks