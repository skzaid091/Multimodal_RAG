class TableStructureProcessor:
    """
    Post-processes Table Transformer structure predictions.

    Responsibilities:
    - Match projected row headers to detected rows
    - Identify rows that function as headers
    - Store row-header relationships for downstream
      table reconstruction

    This stage helps preserve table semantics when
    converting detected structures into structured data.
    """

    def __init__(self, config):
        """
        Store application configuration.
        """

        self.config = config


    def row_overlap(self, row_bbox, header_bbox):
        """
        Compute vertical overlap between a detected row
        and a projected row header.

        Returns:
            overlap_height / row_height

        A value of:
            1.0 -> complete overlap
            0.0 -> no overlap
        """

        row_y1 = row_bbox[1]
        row_y2 = row_bbox[3]

        header_y1 = header_bbox[1]
        header_y2 = header_bbox[3]

        overlap = min(row_y2, header_y2) - max(row_y1, header_y1)

        if overlap <= 0:
            return 0

        row_height = (row_y2 - row_y1)

        return overlap / row_height


    def process(self, structure):
        """
        Associate projected row headers with table rows.

        A row is considered a header row when a projected
        row header overlaps more than 80% of the row's
        height.
        """

        merged_rows = {}

        rows = structure["rows"]

        projected_headers = structure["projected_row_headers"]

        for row_index, row_bbox in enumerate(rows):

            for header_bbox in projected_headers:

                overlap = self.row_overlap(row_bbox, header_bbox)

                # Strong overlap indicates that the
                # projected header belongs to this row.
                if overlap > 0.7:
                    merged_rows[row_index] = header_bbox

                    break

        structure["merged_rows"] = merged_rows

        return structure