import re


class TableCleaner:
    """
    Clean and normalize extracted table data.

    Responsibilities:
    - Normalize OCR text
    - Remove empty rows
    - Merge incorrectly split cells
    - Recalculate table statistics

    This stage improves table quality before
    chunking, indexing, or analysis.
    """


    def _normalize_text(self, text):
        """
        Normalize OCR text.

        Operations:
        - Replace newlines with spaces
        - Collapse repeated whitespace
        - Remove leading/trailing spaces
        """

        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text)

        return text.strip()


    def _is_empty_row(self, row):
        """
        Determine whether a row contains any
        meaningful content.
        """

        return all(
            not cell.strip()
            for cell in row
        )


    def _merge_split_cells(self, row):
        """
        Merge OCR fragments that were incorrectly
        separated into adjacent cells.

        Example:

            [
                '2',
                'Designation',
                'Data Scientist - I',
                'tern'
            ]

        becomes:

            [
                '2',
                'Designation',
                'Data Scientist - Intern'
            ]
        """

        if len(row) < 2:
            return row

        cleaned = []

        i = 0
        while i < len(row):

            current = row[i].strip()

            if (i < len(row) - 1 and current and row[i + 1].strip()):

                #
                # Handle tiny trailing fragments
                # produced by OCR.
                #
                next_text = (
                    row[i + 1]
                    .strip()
                )

                if len(next_text) <= 8:

                    cleaned.append(f"{current} {next_text}")

                    i += 2
                    continue

            cleaned.append(current)
            i += 1

        return cleaned


    def clean(self, table_data):
        """
        Clean a TableData object.

        Operations:
        - Normalize cell text
        - Remove empty rows
        - Update table statistics
        """

        cleaned_rows = []

        for row in table_data.rows:

            # Normalize each cell.
            row = [self._normalize_text(cell) for cell in row]

            # Remove empty rows.
            if self._is_empty_row(row):
                continue

            # Optional OCR repair step.
            # row = self._merge_split_cells(row)

            cleaned_rows.append(row)

        table_data.rows = cleaned_rows

        table_data.row_count = len(cleaned_rows)

        table_data.column_count = max((len(row) for row in cleaned_rows), default=0)

        return table_data


    def process(self, document):
        """
        Clean all extracted tables in the document.
        """

        for element in document.elements:

            if (element.element_type != "table" or element.table_data is None):
                continue

            element.table_data = (
                self.clean(
                    element.table_data
                )
            )

        return document