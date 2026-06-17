import os
from PIL import Image
from uuid import uuid4

from data_models.models import Document, PageContent

class ImageLoader:
    """
    Loads image files and converts them into the
    application's standard Document representation.

    Design:
    Each image is treated as a single-page document
    so that downstream components can process images
    and PDFs through a common interface.
    """

    def __init__(self, config):
        """
        Store application configuration.
        """
        self.config = config


    def _get_unique_document_id(self):
        return str(uuid4()).split("-")[1]
    

    def load(self, original_path, processed_path):
        """
        Load an image file and create a Document object.

        Extracted information:
        - Image dimensions
        - Image format
        - Color mode

        Returns:
            Document
        """

        file_name = os.path.basename(processed_path)

        # Return an error document if the file
        # does not exist.
        if not os.path.exists(processed_path):

            return Document(
                document_id=self._get_unique_document_id(),

                source_type="image",
                document_type="image",

                original_file_path=original_path,
                processed_file_path=processed_path,

                file_name=file_name,
                metadata={},

                page_count=0,
                pages=[],

                error=f"File not found: {processed_path}"
            )

        try:
            # Open image and extract basic metadata.
            with Image.open(processed_path) as image:

                width, height = image.size

                metadata = {
                    "format": image.format,
                    "mode": image.mode
                }

            # Represent the image as a single page.
            page = PageContent(
                page_number=1,
                has_text_layer=False,

                text_blocks=[],

                original_width=width,
                original_height=height,

                image_path=processed_path
            )

            return Document(
                document_id=self._get_unique_document_id(),

                source_type="image",
                document_type="image",

                original_file_path=original_path,
                processed_file_path=processed_path,

                file_name=file_name,
                metadata=metadata,

                page_count=1,
                pages=[page],

                error=None
            )

        except Exception as e:

            # Return a valid Document object
            # containing failure information.
            return Document(
                document_id=self._get_unique_document_id(),

                source_type="image",
                document_type="image",

                original_file_path=original_path,
                processed_file_path=processed_path,

                file_name=file_name,
                metadata={},
                
                page_count=0,
                pages=[],

                error=f"Failed to load image: {e}"
            )