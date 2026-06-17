from .ocr_processor import OCRProcessor
from .pdf_processor import PDFTextExtractor


class TextExtractor:
    """
    Extracts textual content from documents.

    This component acts as a router between:

    - Native PDF text extraction
    - OCR-based text extraction

    Selection is performed on a page-by-page basis
    depending on whether a text layer is available.
    """

    def __init__(self, config, llm_service):
        """
        Initialize text extraction components.
        """

        # Used for scanned documents and images.
        self.ocr_processor = OCRProcessor(config, llm_service)

        # Used for searchable PDFs containing
        # an embedded text layer.
        self.pdf_text_extractor = PDFTextExtractor(config, llm_service)


    def process(self, document):
        """
        Extract text from all document pages.

        Workflow:
        1. Skip document types that do not contain
           page-based text content.
        2. Use native PDF text extraction whenever
           a text layer exists.
        3. Fall back to OCR otherwise.
        """

        # CSV and Excel files are handled through
        # metadata extraction and do not require
        # page-level text processing.
        if document.document_type in {"csv", "excel"}:
            return document

        for page in document.pages:

            # Native PDF text extraction provides
            # higher accuracy and better structure
            # preservation than OCR.
            if page.has_text_layer:
                self.pdf_text_extractor.process_page(document, page)

            # Use OCR for scanned PDFs and images.
            else:
                self.ocr_processor.process_page(document, page)

        return document