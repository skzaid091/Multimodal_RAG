class ReadingOrderBuilder:
    """
    Arrange document elements into reading order.

    Reading order is important for downstream tasks
    such as:

    - Chunk generation
    - Summarization
    - Question Answering
    - Retrieval-Augmented Generation (RAG)

    Elements are sorted using a simple top-to-bottom,
    left-to-right strategy.
    """

    def process(self, document):
        """
        Sort document elements into reading order.

        Sort priority:

            1. Page number
            2. Vertical position (y)
            3. Horizontal position (x)
        """

        document.elements.sort(
            key=lambda element: (
                element.page_number,
                element.bbox[1],
                element.bbox[0]
            )
        )

        return document