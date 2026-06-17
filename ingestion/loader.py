from .document_converter import DocumentConverter

from .pdf_loader import PDFLoader
from .image_loader import ImageLoader

from .excel_loader import ExcelLoader
from .csv_loader import CSVLoader

from .page_renderer import PageRenderer

from mappings.mapping import Mapping

import os
import shutil


class DocumentLoader:
    """
    Central document ingestion component.

    Responsibilities:
    1. Store the original file in the raw documents directory.
    2. Convert supported office documents to PDF.
    3. Route the file to the appropriate loader.
    4. Render PDF pages into images when required.
    5. Return a populated Document object.
    """

    def __init__(self, config):
        """
        Initialize all document processing components.
        """

        self.config = config

        # Handles DOCX/PPTX/ODT/PPT conversion to PDF.
        self.document_converter = DocumentConverter(
            config["converted_documents_dir"]
        )

        # Loaders for different document formats.
        self.pdf_loader = PDFLoader(config)
        self.image_loader = ImageLoader(config)

        self.excel_loader = ExcelLoader(config)
        self.csv_loader = CSVLoader(config)

        # Converts PDF pages into images for downstream processing.
        self.renderer = PageRenderer(config)

        # Mapper
        self.mapper = Mapping(config)


    def _store_in_raw(self, file_path):
        """
        Store a copy of the uploaded document in the
        raw documents directory.

        Keeping an untouched copy is useful for:
        - auditing
        - reprocessing
        - debugging pipeline issues
        """

        raw_dir = self.config["raw_documents_dir"]

        os.makedirs(raw_dir, exist_ok=True)

        file_name = os.path.basename(file_path)

        destination = os.path.join(raw_dir, file_name)

        shutil.copy2(file_path, destination)

        return destination


    def load(self, file_path):
        """
        Load a document into the system.

        Workflow:
        1. Store original file in raw storage.
        2. Convert office documents to PDF if required.
        3. Select the appropriate loader based on file type.
        4. Render PDF pages into images.
        5. Return the constructed Document object.
        """

        # Preserve the original uploaded file.
        raw_file_path = self._store_in_raw(file_path)

        # By default, processing is performed on the raw file.
        processed_file_path = raw_file_path

        # Track both the original and current extension.
        original_ext = os.path.splitext(file_path)[1].lower()
        ext = original_ext

        # Convert supported office documents into PDF so the
        # rest of the pipeline can process them uniformly.
        if ext in self.config["CONVERTIBLE_TYPES"]:

            processed_file_path = (
                self.document_converter.convert_to_pdf(
                    raw_file_path
                )
            )

            ext = ".pdf"

        # PDF Processing
        if ext == ".pdf":

            document = self.pdf_loader.load(
                raw_file_path,
                processed_file_path,
                original_ext,
                ext
            )

            # Generate page images required by OCR,
            # layout analysis, and multimodal models.
            document = self.renderer.render(document, self.mapper)

        # Image Processing
        elif ext in self.config["IMAGE_TYPES"]:

            document = self.image_loader.load(
                raw_file_path,
                processed_file_path
            )

        # Spreadsheet Processing
        elif ext in self.config["EXCEL_TYPES"]:

            document = self.excel_loader.load(
                raw_file_path,
                processed_file_path
            )

        # CSV Processing
        elif ext in self.config["CSV_TYPES"]:

            document = self.csv_loader.load(
                raw_file_path,
                processed_file_path
            )

        # Unsupported format
        else:

            raise ValueError(f"Unsupported file type: {ext}")
        
        if not document.error:
            self.mapper.add_document_id_mapping(
                document.file_name, 
                document.document_id, 
                document_data={
                    "original_file_path": document.original_file_path, 
                    "processed_file_path": document.processed_file_path, 
                }
            )
            
        return document