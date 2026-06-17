class ConversationMemory:
    """
    In-memory conversation history manager.

    Responsible for:
    - Storing user-assistant interactions
    - Limiting history size
    - Providing conversation history
    - Clearing stored history
    - Updating history configuration at runtime
    """

    def __init__(self, max_history=5):

        # Maximum number of interactions
        # retained in memory
        self.max_history = max_history

        # Conversation history storage
        self.history = []


    def add_interaction(self, user_query, assistant_response):
        """
        Store a new user-assistant interaction.

        If the history exceeds the configured
        maximum size, the oldest interaction
        is removed.
        """

        self.history.append(
            {
                "user": user_query,
                "assistant": assistant_response
            }
        )

        # Keep only the most recent interactions
        if len(self.history) > self.max_history:
            self.history.pop(0)


    def get_history(self):
        """
        Retrieve the current conversation history.

        Returns:
            list:
                Copy of stored interactions.
        """

        return self.history.copy()


    def clear_memory(self):
        """
        Remove all stored conversation history.
        """

        self.history.clear()


    def update_conf_and_history(self, new_max_history):
        """
        Update the maximum conversation history
        size and trim existing history if needed.

        Args:
            new_max_history (int):
                New maximum number of interactions
                to retain.
        """

        self.max_history = new_max_history

        # Keep only the most recent interactions
        self.history = self.history[-self.max_history:]