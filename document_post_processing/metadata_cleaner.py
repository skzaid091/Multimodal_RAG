class MetadataCleaner:

    """
    Remove temporary processing metadata
    once all extraction stages are complete.
    """

    def process(self, document):

        for element in document.elements:

            if hasattr(element, "metadata"):
                del element.metadata

        return document