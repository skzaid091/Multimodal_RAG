from uuid import uuid4

from data_models.models import DocumentChunk


class TableChunker:
    """
    Build retrievable chunks from tables.

    Responsibilities:
    - Convert table rows into text.
    - Preserve section context.
    - Preserve table metadata.
    - Create a single chunk per table.
    """

    def __init__(self, config):

        self.config = config

        self.table_no = 1


    def process(self, element, section, document_id):
        """
        Create a chunk from a table element.

        Parameters:
            element: Table element.

            section: Parent section.

        Returns:
            List[DocumentChunk]
        """

        table_data = element.table_data

        if not table_data:
            return []

        rows = table_data.rows

        if not rows:
            return []

        content = self._rows_to_text(rows, self.table_no)

        chunk = DocumentChunk(

            document_id = document_id,

            chunk_id=str(uuid4()).split("-")[-1],

            chunk_index=-1,

            chunk_type="table",

            section_title=section["title"],

            page_number=element.page_number,

            content=content,

            metadata={
                "crop_path": table_data.image_path,
                "table_no": self.table_no
            }
        )

        self.table_no += 1

        return [chunk]
    

    def _rows_to_text(self, rows, table_no):
        """
        Convert table rows into
        retrievable text.

        Example:

            [
                ["A", "B"],
                ["1", "2"]
            ]

        Becomes:

            A | B
            1 | 2
        """
        lines = [f"Table {table_no}", ""]

        for row in rows:
            values = [str(cell).strip() for cell in row]
            lines.append(" | ".join(values))

        return "\n".join(lines)