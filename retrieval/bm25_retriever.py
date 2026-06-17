class BM25Retriever:

    def __init__(self, bm25_store):

        self.bm25_store = bm25_store


    def retrieve(self, query, top_k=10):

        return self.bm25_store.search(
            query=query,
            top_k=top_k
        )