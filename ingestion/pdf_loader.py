import os
import pymupdf

from uuid import uuid4 
from data_models.models import Document, PageContent


class PDFLoader:
    """
    Loads PDF documents and converts them into the
    application's standard Document representation.

    Responsibilities:
    - Extract document metadata
    - Extract page text
    - Extract text blocks with coordinates
    - Collect page dimensions
    - Create PageContent objects
    - Return a populated Document instance
    """

    def __init__(self, config):
        """
        Initialize loader configuration and ensure
        the page image directory exists.
        """

        self.config = config

        os.makedirs(
            config["document_images_dir"],
            exist_ok=True
        )
    

    def _get_unique_document_id(self):
        return str(uuid4()).split("-")[1]


    def _extract_text_blocks(self, page):
        """
        Extract text blocks together with their bounding boxes.

        These blocks preserve layout information and are useful
        for downstream tasks such as:
        - Layout analysis
        - OCR fallback
        - Chunking
        - Context reconstruction
        """

        blocks = []

        for block in page.get_text("dict")["blocks"]:

            # Skip image-only blocks.
            if "lines" not in block:
                continue

            text_parts = []

            # Collect all text spans belonging
            # to the current block.
            for line in block["lines"]:
                for span in line["spans"]:
                    text_parts.append(span["text"])

            text = " ".join(text_parts).strip()

            # Ignore empty blocks.
            if not text:
                continue

            blocks.append(
                {
                    "text": text,
                    "bbox": block["bbox"]
                }
            )

        return blocks


    def load(self, original_path, processed_path, original_ext, converted_ext):
        """
        Load a PDF and convert it into a Document object.

        Args:
            original_path:
                Original uploaded file.

            processed_path:
                PDF file used for processing.

            original_ext:
                Original file extension.

            converted_ext:
                Extension after conversion.

        Returns:
            Document
        """

        file_name = os.path.basename(processed_path)

        # Return an error document if the PDF
        # does not exist.
        if not os.path.exists(processed_path):

            return Document(
                document_id=self._get_unique_document_id(),

                source_type=original_ext[1:],
                document_type=converted_ext[1:],

                original_file_path=original_path,
                processed_file_path=processed_path,

                file_name=file_name,
                metadata={},

                page_count=0,
                pages=[],

                error=f"File not found: {processed_path}"
            )

        try:
            # Open PDF using PyMuPDF.
            with pymupdf.open(processed_path) as doc:

                # Extract document-level metadata.
                raw_metadata = dict(doc.metadata)
                metadata = {
                    "title": raw_metadata.get("title"),
                    "author": raw_metadata.get("author"),
                    "subject": raw_metadata.get("subject"),
                }

                pages = []

                for page in doc:

                    # Extract page text.
                    text = page.get_text("text").strip()

                    # Determine whether the page
                    # contains a native text layer.
                    page_has_text_layer = bool(text)

                    # Extract structured text blocks.
                    text_blocks = self._extract_text_blocks(page)

                    # Original PDF page dimensions.
                    rect = page.rect

                    pages.append(
                        PageContent(
                            page_number=page.number + 1,
                            has_text_layer=page_has_text_layer,

                            text_blocks=text_blocks,

                            original_width=rect.width,
                            original_height=rect.height,
                        )
                    )

                return Document(
                    document_id=self._get_unique_document_id(),

                    source_type=original_ext[1:],
                    document_type=converted_ext[1:],

                    original_file_path=original_path,
                    processed_file_path=processed_path,

                    file_name=file_name,
                    metadata=metadata,

                    page_count=len(doc),
                    pages=pages,

                    error=None
                )
        


        except Exception as e:

            # Capture unexpected failures and
            # return a valid Document object
            # containing error information.
            import traceback
            traceback.print_exc()

            return Document(
                document_id=self._get_unique_document_id(),

                source_type=original_ext[1:],
                document_type=converted_ext[1:],

                original_file_path=original_path,
                processed_file_path=processed_path,

                file_name=file_name,
                metadata={},

                page_count=0,
                pages=[],

                error=f"Failed to open PDF: {e}"
            )