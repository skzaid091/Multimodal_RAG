from .element_cleaner import ElementCleaner
from .reading_order_builder import ReadingOrderBuilder
from .figure_cleaner import FigureCleaner
from .metadata_cleaner import MetadataCleaner


class DocumentCleaner:
    """
    Final document post-processing pipeline.

    Responsibilities:
    - Clean extracted document elements
    - Remove invalid or duplicate content
    - Clean figure metadata
    - Establish reading order

    This stage transforms raw extracted elements
    into a cleaner document structure suitable for
    chunking, indexing, and retrieval.
    """

    def __init__(self, config):
        """
        Initialize document cleaning components.
        """

        self.config = config

        # Cleans document elements by:
        # - Removing duplicate detections
        # - Removing invalid elements
        # - Normalizing extracted text
        self.element_cleaner = ElementCleaner()

        # Builds a logical reading order
        # across extracted document elements.
        self.reading_order_builder = ReadingOrderBuilder()

        # Cleans and enriches figure metadata.
        self.figure_cleaner = FigureCleaner()

        # Cleans unnecessary metadata
        self.metadata_cleaner = MetadataCleaner()


    def process(self, document):
        """
        Execute the complete document cleaning
        pipeline.

        Workflow:

            Raw Elements
                  ↓

            ElementCleaner
                  ↓

            FigureCleaner
                  ↓

         ReadingOrderBuilder
                  ↓

            Clean Document
        """

        # Remove duplicate elements,
        # discard invalid elements,
        # and normalize extracted text.
        document = self.element_cleaner.process(document)

        # Clean figure metadata and
        # prepare figures for retrieval.
        document = self.figure_cleaner.process(document)

        # Cleans metadata
        document = self.metadata_cleaner.process(document)

        # Arrange elements into the
        # natural document reading order.
        document = self.reading_order_builder.process(document)

        return document