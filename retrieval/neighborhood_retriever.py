class NeighborhoodRetriever:

    def __init__(self, chunk_retriever, before=1, after=1):

        self.chunk_retriever = chunk_retriever

        self.before = before
        self.after = after


    def retrieve(self, chunks):

        expanded_chunks = {}

        for chunk in chunks:

            document_id = chunk["document_id"]

            document_chunks = self.chunk_retriever._load_document(document_id)

            chunk_index = chunk["chunk_index"]

            start = max(0, chunk_index - self.before)

            end = min(len(document_chunks), chunk_index + self.after + 1)

            for neighbor in document_chunks[start:end]:

                key = (
                    neighbor["document_id"],
                    neighbor["chunk_id"]
                )

                expanded_chunks[key] = (
                    neighbor
                )

        results = list(expanded_chunks.values())

        results.sort(
            key=lambda x: (
                x["document_id"],
                x["chunk_index"]
            )
        )

        return results