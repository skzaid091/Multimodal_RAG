import os
import pandas as pd
from uuid import uuid4

from data_models.models import Document



class CSVLoader:
    """
    Loads CSV files and converts them into the
    application's standard Document representation.

    Current behavior:
    - Validates file existence
    - Extracts basic dataset metadata
    - Returns a Document object

    Note:
    CSV files do not have pages or layout information,
    so page-related fields remain empty.
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
        Load a CSV file and extract basic metadata.

        Metadata extracted:
        - Column names
        - Number of columns

        Returns:
            Document
        """

        file_name = os.path.basename(processed_path)

        # Return an error document if the file
        # does not exist.
        if not os.path.exists(processed_path):

            return Document(
                document_id=self._get_unique_document_id(),

                source_type="csv",
                document_type="csv",

                original_file_path=original_path,
                processed_file_path=processed_path,

                file_name=file_name,
                metadata={},

                page_count=0,
                pages=[],

                error=f"File not found: {processed_path}"
            )

        try:

            # Read only a small sample of rows.
            # We only need schema information here,
            # not the full dataset.
            df = pd.read_csv(processed_path, nrows=5)

            # Dataset-level metadata.
            metadata = {
                "columns": list(df.columns),
                "column_count": len(df.columns)
            }

            return Document(
                document_id=self._get_unique_document_id(),

                source_type="csv",
                document_type="csv",

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

                source_type="csv",
                document_type="csv",

                original_file_path=original_path,
                processed_file_path=processed_path,

                file_name=file_name,
                metadata={},

                page_count=0,
                pages=[],

                error=f"Failed to load csv file: {e}"
            )