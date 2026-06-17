import cv2


class TableOCR:
    """
    Extract text from table cells.

    Responsibilities:
    - Crop individual cell regions
    - Run OCR on each cell
    - Populate TableCell.text

    This stage combines:
    - Table structure from TATR
    - OCR text extraction

    to produce text-filled table cells.
    """

    def __init__(self, config, ocr_processor):
        """
        Initialize OCR dependencies.

        A shared OCRProcessor instance is injected
        to avoid loading multiple OCR models.
        """

        self.config = config

        self.ocr_processor = ocr_processor


    def extract_cell_text(self, table_image, cell):
        """
        Extract text from a single table cell.
        """

        x1, y1, x2, y2 = map(int, cell.bbox)

        # Remove a small border around the cell
        # to avoid grid lines interfering with OCR.
        padding = self.config.get("table_cell_padding", 2)

        x1 = max(0, x1 + padding)
        y1 = max(0, y1 + padding)

        x2 = max(x1 + 1, x2 - padding)
        y2 = max(y1 + 1, y2 - padding)

        crop = table_image[y1:y2, x1:x2]

        # Ignore invalid crops.
        if crop.size == 0:
            return ""

        try:
            text = self.ocr_processor._extract_text(crop)
            return text.strip()

        except Exception as e:
            print(f"[TableOCR] OCR failed: {e}")
            return ""


    def process_table(self, element):
        """
        Run OCR on all cells belonging to a table.
        """

        crop_path = element.metadata.get("table_crop_path")
        if not crop_path:
            return

        table_image = cv2.imread(crop_path)

        if table_image is None:
            return

        cells = element.metadata.get("table_cells", [])

        for cell in cells:
            cell.text = self.extract_cell_text(table_image, cell)

        # Store updated cells.
        element.metadata["table_cells"] = cells



    def process(self, document):
        """
        Run table OCR across all detected tables.
        """

        for element in document.elements:

            if  element.element_type != "table":
                continue

            self.process_table(element)

        return document