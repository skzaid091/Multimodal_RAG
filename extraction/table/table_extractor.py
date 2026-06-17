from .table_image_extractor import TableImageExtractor
from .tatr_extractor import TATRExtractor
from extraction.ocr_processor import OCRProcessor
from .table_ocr import TableOCR
from .table_data_builder import TableDataBuilder

from extraction.ocr_correction.ocr_table_correction import TableLLMCorrector


class TableExtractor:
    """
    End-to-end table extraction pipeline.

    Workflow:

        Detected Table Region
                    ↓
          TableImageExtractor
                    ↓
            Cropped Table Image
                    ↓
             TATRExtractor
                    ↓
        Table Structure Detection
           (rows / columns / cells)
                    ↓
                TableOCR
                    ↓
          Cell Text Extraction
                    ↓
           TableDataBuilder
                    ↓
          Structured TableData
    """

    def __init__(self, config, llm_service):
        """
        Initialize all table-processing components.
        """

        self.config = config

        self.enable_ocr_correction = config.get("enable_ocr_correction", False)

        # Extract table regions from document pages.
        self.table_image_extractor = TableImageExtractor(config)

        # Detect table structure using
        # Microsoft's Table Transformer.
        self.tatr_extractor = TATRExtractor(config)

        # Perform OCR on detected table cells.
        self.table_ocr = TableOCR(config, OCRProcessor(config, llm_service))

        # Convert OCR results into a structured
        # TableData representation.
        self.table_data_builder = TableDataBuilder(config)

        self.table_llm_corrector = TableLLMCorrector(config, llm_service)


    def process(self, document):
        """
        Execute the complete table extraction pipeline.
        """

        # Crop detected table regions.
        document = self.table_image_extractor.process(document)

        # Detect rows, columns, and cells.
        document = self.tatr_extractor.process(document)

        # Extract text from table cells.
        document = self.table_ocr.process(document)

        # Build structured table data.
        document = self.table_data_builder.process(document)

        if self.enable_ocr_correction:
            document = self.table_llm_corrector.process(document)

        return document