class FigureCleaner:
    """
    Remove low-value figure elements from the document.

    Some detected figures provide little retrieval
    value and can safely be discarded.

    Examples:
        - Signatures
        - Stamps

    This reduces noise before chunking,
    indexing, and retrieval.
    """

    USELESS_TYPES = {
        "signature",
        "stamp",
    }


    def process(self, document):
        """
        Filter figure elements based on the
        figure type predicted by the VLM.
        """

        filtered = []

        for element in document.elements:

            # Keep all non-figure elements.
            if element.element_type != "figure":
                filtered.append(element)
                continue

            # Skip figures that failed
            # caption generation.
            if not element.figure_data:
                continue

            # Remove low-value figures.
            if element.figure_data.figure_type in self.USELESS_TYPES:
                continue

            filtered.append(element)

        document.elements = filtered

        return document