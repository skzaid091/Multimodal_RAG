import re
import cv2
import unicodedata

from .ocr_correction.ocr_text_correction import TextLLMCorrector


class OCRProcessor:
    """
    Extracts text from image-based document regions.

    Used when a document page does not contain a
    native text layer, such as:

    - Scanned PDFs
    - Photographs
    - Screenshots
    - Image-only documents

    Processing Flow:

        Layout Element
              ↓
        Crop Image Region
              ↓
        OCR Engine
              ↓
        Text Cleanup
              ↓
        Optional LLM Correction
              ↓
        DocumentElement.text
    """

    def __init__(self, config, llm_service):
        """
        Initialize the configured OCR engine and
        optional OCR correction service.
        """

        self.config = config
        self.llm_service = llm_service

        self.enable_ocr_correction = config.get("enable_ocr_correction", False)
        self.text_llm_corrector = TextLLMCorrector(config, llm_service)

        if config["ocr_type"] == "EasyOCR":
            import easyocr
            self.ocr = easyocr.Reader([config["ocr_language"]])

        elif config["ocr_type"] == "PaddleOCR":
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(lang=config["ocr_language"], use_angle_cls=config[ "ocr_use_angle_cls"])

        else:
            raise ValueError(f"Unsupported OCR type: " f"{config['ocr_type']}")


    def _post_process(self, text):
        """
        Perform lightweight OCR cleanup.

        This stage removes common OCR formatting
        artifacts while preserving the original
        document content.
        """

        if not text:
            return ""

        # Normalize unicode representations such as
        # ligatures and full-width characters.
        text = unicodedata.normalize("NFKC", text)

        # Normalize line endings.
        text = text.replace("\r\n", "\n")

        # Remove trailing whitespace from lines.
        text = "\n".join(line.strip() for line in text.splitlines())

        # Collapse excessive blank lines.
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Collapse repeated spaces and tabs.
        text = re.sub(r"[ \t]+", " ", text)

        return text.strip()


    def _easyocr(self, image):
        """
        Extract text using EasyOCR.
        """

        try:
            results = self.ocr.readtext(
                image,
                detail=0
            )
            return "\n".join(results)

        except Exception as e:
            print(f"OCR failed: {e}")
            return ""


    def _paddleocr(self, image):
        """
        Extract text using PaddleOCR.
        """
        pass


    def _rapidocr(self, image):
        """
        Placeholder for RapidOCR support.
        """
        pass


    def _extract_text(self, image):
        """
        Route OCR requests to the configured
        OCR engine and apply standard cleanup.
        """

        if self.config["ocr_type"] == "EasyOCR":
            text = self._easyocr(image)

        elif self.config["ocr_type"] == "PaddleOCR":
            text = self._paddleocr(image)

        else:
            text = ""

        return self._post_process(text)


    def _get_cropped_image(self, page_image, bbox):
        """
        Crop an element region from the rendered
        page image.

        Bounding coordinates are clipped to image
        boundaries to prevent invalid indexing.
        """

        x1, y1, x2, y2 = map(int, bbox)

        height, width = page_image.shape[:2]

        x1 = max(0, min(x1, width))
        x2 = max(0, min(x2, width))

        y1 = max(0, min(y1, height))
        y2 = max(0, min(y2, height))

        return page_image[y1:y2, x1:x2]


    def process_page(self, document, page):
        """
        Populate text content for all OCR-based
        text regions detected on the page.

        Processing Flow:

            Text Element
                  ↓
            Crop Region
                  ↓
            OCR
                  ↓
            Text Cleanup
                  ↓
            Optional LLM Correction
                  ↓
            element.text
        """

        page_image = cv2.imread(page.image_path)

        page_elements = [
            element
            for element in document.elements
            if (
                element.page_number == page.page_number
            )
        ]

        # Collect OCR-derived elements so they can
        # be corrected in a single LLM request.
        ocr_elements = []

        for element in page_elements:

            # Skip non-textual layout regions such
            # as tables, figures, and images.
            if element.element_type not in self.config["TEXT_ELEMENT_TYPES"]:
                continue

            crop = self._get_cropped_image(page_image, element.bbox)

            # Ignore invalid crops.
            if crop.size == 0:
                continue

            # Extract OCR text and attach it to
            # the corresponding layout element.
            text = self._extract_text(crop)

            element.text = text

            ocr_elements.append(element)

        # Improve OCR quality using an LLM after
        # all regions on the page have been
        # processed.
        if self.enable_ocr_correction and ocr_elements:
            self.text_llm_corrector.correct_text(ocr_elements)

        return document