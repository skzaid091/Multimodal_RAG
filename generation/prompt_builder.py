class PromptBuilder:

    def __init__(self, config):

        self.config = config

        # --------------------------------------------------
        # Precise Response Prompts
        # --------------------------------------------------

        self.PRECISE_PROMPT_WITHOUT_HISTORY = """
        You are a helpful AI assistant.

        Answer the user's question using only the retrieved context.

        Requirements:
        1. Give a concise and direct answer.
        2. Focus only on information relevant to the question.
        3. Do not include unrelated details.
        4. If the answer is not present in the context, say so.
        5. Do not use outside knowledge.

        Retrieved Context:
        {context}

        Question:
        {query}

        Answer:
        """

        self.PRECISE_PROMPT_WITH_HISTORY = """
        You are a helpful AI assistant.

        Use the conversation history only to understand
        the user's intent and references.

        Answer the user's question using only the retrieved context.

        Requirements:
        1. Give a concise and direct answer.
        2. Focus only on information relevant to the question.
        3. Do not include unrelated details.
        4. If the answer is not present in the context, say so.
        5. Do not use outside knowledge.

        Conversation History:
        {history}

        Retrieved Context:
        {context}

        Question:
        {query}

        Answer:
        """

        # --------------------------------------------------
        # Detailed Response Prompts
        # --------------------------------------------------

        self.DETAILED_PROMPT_WITHOUT_HISTORY = """
        You are a helpful AI assistant.

        Answer the user's question using only the retrieved context.

        Requirements:
        1. Provide a detailed and complete answer.
        2. Explain relevant concepts and relationships.
        3. Use structured formatting when helpful.
        4. Include important supporting details.
        5. If the answer is not present in the context, say so.
        6. Do not use outside knowledge.

        Retrieved Context:
        {context}

        Question:
        {query}

        Answer:
        """

        self.DETAILED_PROMPT_WITH_HISTORY = """
        You are a helpful AI assistant.

        Use the conversation history only to understand
        the user's intent and references.

        Answer the user's question using only the retrieved context.

        Requirements:
        1. Provide a detailed and complete answer.
        2. Explain relevant concepts and relationships.
        3. Use structured formatting when helpful.
        4. Include important supporting details.
        5. If the answer is not present in the context, say so.
        6. Do not use outside knowledge.

        Conversation History:
        {history}

        Retrieved Context:
        {context}

        Question:
        {query}

        Answer:
        """


    def build(self, retrieval_context, query, history=None):

        if self.config["response_mode"] == "detailed":
            prompt = self.DETAILED_PROMPT_WITH_HISTORY if history else self.DETAILED_PROMPT_WITHOUT_HISTORY

        else:
            prompt = self.PRECISE_PROMPT_WITH_HISTORY if history else self.PRECISE_PROMPT_WITHOUT_HISTORY
        
        return prompt.format(
            history=history or "",
            context=retrieval_context,
            query=query,
        )   