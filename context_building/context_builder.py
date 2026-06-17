from .conversation_memory import ConversationMemory


class ContextBuilder:
    """
    Builds the final context passed to the LLM.

    Responsible for:
    - Managing conversation history
    - Formatting retrieval results
    - Constructing the final generation context
    """

    def __init__(self, config):

        # Maximum number of retrieved chunks included in context
        self.max_chunks = config["context_max_chunks"]

        # Conversation memory manager
        self.memory = ConversationMemory(
            config["conversation_max_history"]
        )


    def build_history_context(self):
        """
        Convert stored conversation history into
        a formatted text block.
        """

        history = self.memory.get_history()

        if not history:
            return ""

        context = ""

        for item in history:

            context += (
                f"User: {item['user']}\n"
                f"Assistant: {item['assistant']}\n\n"
            )

        return context


    def update_memory(self, query, response):
        """
        Store the latest user interaction.
        """

        self.memory.add_interaction(
            query,
            response
        )

    def update_memory_conf_and_history(self, new_max_history):
        self.memory.update_conf_and_history(new_max_history)


    def clear_memory(self):
        """
        Remove all stored conversation history.
        """

        self.memory.clear_memory()


    def build(self, query, chunks, query_rewriting=False):
        """
        Build the final context object used for
        response generation.

        Includes:
        - User query
        - Conversation history
        - Retrieved document context
        """

        # Restrict context to configured chunk limit
        chunks = chunks[:self.max_chunks]

        context_parts = []

        # Format retrieved chunks
        for chunk in chunks:

            context_parts.append(
                f"[{chunk['chunk_type'].upper()}]\n"
                f"Section: {chunk['section_title']}\n\n"
                f"{chunk['content']}"
            )

        context = "\n\n".join(context_parts)

        history = None

        # If query rewriting is disabled,
        # include conversation history in generation context
        if not query_rewriting:
            history = self.build_history_context()

        return {
            "query": query,
            "history": history,
            "retrieval_context": context
        }