from data_models.models import TableCell


class TableCellGenerator:
    """
    Generate logical table cells from detected
    table structure.

    Responsibilities:
    - Combine rows and columns into cell regions
    - Handle merged rows
    - Create TableCell objects
    - Preserve row/column indexing

    Output:
        List[TableCell]
    """


    def generate(self, structure):
        """
        Generate table cells from the detected
        table structure.
        """

        rows = structure["rows"]
        columns = structure["columns"]

        merged_rows = structure.get("merged_rows", {})

        cells = []

        #
        # Iterate through all detected rows.
        #
        for row_index, row_bbox in enumerate(rows):

            row_y1 = row_bbox[1]
            row_y2 = row_bbox[3]

            #
            # Handle merged rows.
            #
            # These rows span all columns and
            # therefore become a single cell.
            #
            if row_index in merged_rows:

                cells.append(
                    TableCell(
                        row_index=row_index,
                        column_index=0,

                        bbox=[
                            columns[0][0],
                            row_y1,
                            columns[-1][2],
                            row_y2
                        ],

                        colspan=len(columns)
                    )
                )

                continue

            #
            # Generate regular cells by combining
            # the current row with each column.
            #
            for column_index, column_bbox in enumerate(columns):

                col_x1 = column_bbox[0]
                col_x2 = column_bbox[2]

                cell_bbox = [
                    col_x1,
                    row_y1,
                    col_x2,
                    row_y2
                ]

                cells.append(
                    TableCell(
                        row_index=row_index,
                        column_index=column_index,

                        bbox=cell_bbox
                    )
                )

        return cells