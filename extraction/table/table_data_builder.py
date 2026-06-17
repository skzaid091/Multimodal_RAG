from collections import defaultdict

from data_models.models import TableData
from cleaner.table_cleaner import TableCleaner


class TableDataBuilder:
    """
    Convert OCR-populated table cells into a
    structured TableData object.

    Responsibilities:
    - Group cells by row
    - Sort cells into reading order
    - Build row-wise table representation
    - Generate table statistics
    - Run table cleaning and normalization
    """

    def __init__(self, config):
        """
        Initialize table post-processing components.
        """

        self.config = config

        # Cleans and normalizes extracted tables.
        self.table_cleaner = TableCleaner()


    def build(self, cells, image_path):
        """
        Construct a TableData object from a list
        of TableCell instances.
        """

        if not cells:
            return TableData()

        rows_dict = defaultdict(list)

        #
        # Group cells by row index.
        #
        for cell in cells:
            rows_dict[cell.row_index].append(cell)

        table_rows = []

        #
        # Process rows in visual order.
        #
        for row_index in sorted( rows_dict.keys()):

            row_cells = sorted(
                rows_dict[row_index],
                key=lambda c: c.column_index
            )

            # Convert row cells into a list
            # of textual values.
            row_data = [cell.text.strip() for cell in row_cells]

            table_rows.append(row_data)

        # Determine maximum row width.
        column_count = max(
            len(row)
            for row in table_rows
        )

        return TableData(
            headers=[],
            title=None,

            rows=table_rows,

            row_count=len(table_rows),
            column_count=column_count,

            image_path=image_path
        )


    def process(self, document):
        """
        Build structured table data for all
        detected tables in the document.
        """

        for element in document.elements:

            if element.element_type != "table":
                continue 

            table_data = self.build(element.metadata["table_cells"], element.metadata["table_crop_path"])

            # Normalize extracted table content.
            table_data = self.table_cleaner.clean(table_data)

            element.table_data = table_data

        return document