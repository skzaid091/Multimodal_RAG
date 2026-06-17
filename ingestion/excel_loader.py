import os
import pandas as pd
from uuid import uuid4

from data_models.models import Document


class ExcelLoader:
    """
    Loads Excel spreadsheets and converts them into the
    application's standard Document representation.

    Current behavior:
    - Validates file existence
    - Extracts workbook metadata
    - Returns a Document object

    Note:
    Excel files do not contain pages in the same sense as
    PDFs, therefore page-related fields remain empty.
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
        Load an Excel workbook and extract basic metadata.

        Metadata extracted:
        - Sheet names
        - Number of sheets

        Returns:
            Document
        """

        file_name = os.path.basename(processed_path)

        # Return an error document if the file
        # does not exist.
        if not os.path.exists(processed_path):

            return Document(
                document_id=self._get_unique_document_id(),

                source_type="excel",
                document_type="excel",

                original_file_path=original_path,
                processed_file_path=processed_path,

                file_name=file_name,
                metadata={},

                page_count=0,
                pages=[],

                error=f"File not found: {processed_path}"
            )

        try:
            # Open workbook without loading all sheet
            # contents into memory.
            excel_file = pd.ExcelFile(
                processed_path
            )

            # Workbook-level metadata.
            metadata = {
                "sheet_names": excel_file.sheet_names,
                "sheet_count": len(
                    excel_file.sheet_names
                )
            }

            return Document(
                document_id=self._get_unique_document_id(),

                source_type="excel",
                document_type="excel",

                original_file_path=original_path,
                processed_file_path=processed_path,

                file_name=file_name,
                metadata=metadata,

                page_count=0,
                pages=[],

                error=None
            )

        except Exception as e:

            # Return a valid Document object
            # containing failure information.
            return Document(
                document_id=self._get_unique_document_id(),

                source_type="excel",
                document_type="excel",

                original_file_path=original_path,
                processed_file_path=processed_path,

                file_name=file_name,
                metadata={},

                page_count=0,
                pages=[],

                error=f"Failed to load excel file: {e}"
            )