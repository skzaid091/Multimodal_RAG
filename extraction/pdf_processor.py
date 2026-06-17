from extraction.ocr_correction.ocr_text_correction import TextLLMCorrector

class PDFTextExtractor:
    """
    Extracts text for layout elements from PDFs that
    already contain a searchable text layer.

    Workflow:
    1. Convert PDF text block coordinates into
       rendered-image coordinates.
    2. Match text blocks to detected layout elements.
    3. Aggregate matching text.
    4. Populate DocumentElement.text.
    """

    def __init__(self, config, llm_service):
        """
        Store application configuration.
        """
        self.config = config

        self.text_llm_corrector = TextLLMCorrector(config, llm_service)


    def _overlap_ratio(self, element_bbox, block_bbox):
        """
        Compute how much of a text block is covered
        by a detected layout element.

        Returns:
            intersection_area / block_area

        Using block coverage rather than IoU helps
        determine whether a text block belongs to a
        particular layout region.
        """

        x_left = max(element_bbox[0], block_bbox[0])
        y_top = max(element_bbox[1], block_bbox[1])

        x_right = min(element_bbox[2], block_bbox[2])
        y_bottom = min(element_bbox[3], block_bbox[3])

        if (x_right <= x_left or y_bottom <= y_top):
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        block_area = (block_bbox[2] - block_bbox[0]) * (block_bbox[3] - block_bbox[1])

        if block_area <= 0:
            return 0.0

        return (
            intersection_area
            / block_area
        )


    def _scale_bbox(self, pdf_bbox, page):
        """
        Convert PDF coordinates into rendered-image
        coordinates.

        Layout detection operates on rendered page
        images, therefore PDF text blocks must be
        mapped into the same coordinate system.
        """

        scale_x = page.rendered_width / page.original_width
        scale_y = page.rendered_height / page.original_height

        return [
            pdf_bbox[0] * scale_x,
            pdf_bbox[1] * scale_y,
            pdf_bbox[2] * scale_x,
            pdf_bbox[3] * scale_y,
        ]


    def extract(self, element, page):
        """
        Extract text belonging to a layout element.

        A text block is assigned to an element when
        more than 50% of the block lies inside the
        element's bounding box.
        """

        matched_blocks = []

        for block in page.text_blocks:

            scaled_bbox = self._scale_bbox(block["bbox"], page)

            overlap = self._overlap_ratio(element.bbox, scaled_bbox)
            if overlap > 0.5:

                matched_blocks.append(
                    (
                        scaled_bbox[1],
                        block["text"]
                    )
                )

        # Preserve top-to-bottom reading order.
        matched_blocks.sort(key=lambda item: item[0])

        return "\n".join(text for _, text in matched_blocks)
    

    def modify_element_text(self, element_type, element_text):
        
        if element_type in ["isolate_formula", "formula"]:
            return self.text_llm_corrector.generate_formula_description(element_text)


    def process_page(self, document, page):
        """
        Populate text content for all text-based
        layout elements on a page.
        """

        page_elements = [
            element
            for element in document.elements
            if (
                element.page_number == page.page_number
            )
        ]

        for element in page_elements:

            # Skip non-textual elements such as
            # tables, figures, and images.
            if (element.element_type not in self.config["TEXT_ELEMENT_TYPES"]):
                continue

            element.text = self.extract(element, page)

            if (element.element_type not in self.config["generate_element_description"] or not element.text):
                continue

            element.text = self.modify_element_text(element.element_type, element.text)

        return document