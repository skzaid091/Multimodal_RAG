from .figure_image_extractor import FigureImageExtractor
from .figure_captioner import FigureCaptioner

class FigureExtractor:
    """
    End-to-end figure understanding pipeline.

    Responsibilities:
    - Extract figure regions from pages
    - Generate figure captions
    - Populate FigureData objects

    Workflow:

        Figure Element
               ↓
        FigureImageExtractor
               ↓
          Cropped Figure
               ↓
        Figure Captioner
               ↓
           FigureData
    """

    def __init__(self, config, vlm_service):
        """
        Initialize figure extraction components.
        """

        self.config = config

        # Responsible for cropping figure regions
        # from rendered document pages.
        self.figure_image_extractor = FigureImageExtractor(config)

        # API based Image Captioner
        self.figure_captioner = FigureCaptioner(config, vlm_service)


    def process(self, document):
        """
        Process all figure elements in the document.

        Operations:
        1. Extract figure crops.
        2. Generate captions.
        3. Attach FigureData to elements.
        """

        # Extract figure images first.
        document = self.figure_image_extractor.process(document)

        for element in document.elements:

            if element.element_type != "figure" or not element.image_path:
                continue

            # Generate figure description.
            figure_data = self.figure_captioner.caption(element.image_path)

            element.figure_data = figure_data

        return document