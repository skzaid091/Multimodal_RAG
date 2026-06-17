class QueryRewriter:

    def __init__(self, llm_service):
        self.llm_service = llm_service


    def rewrite(self, history, query):

        if not history:
            return query

        prompt = f"""Convert the user's latest question into a standalone question.

        Use the conversation history only to resolve references such as:
        - it
        - this
        - that
        - they
        - the model
        - the method

        Return ONLY the rewritten question.

        Conversation History:
        {history}

        Latest Question:
        {query}

        Standalone Question:
        """

        rewritten_query = self.llm_service.invoke(
            prompt
        )

        return rewritten_query.strip()