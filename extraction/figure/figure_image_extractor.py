import os
import cv2
from uuid import uuid4

from mappings.mapping import Mapping


class FigureImageExtractor:
    """
    Extract figure regions from document pages.

    Responsibilities:
    - Crop detected figure regions
    - Save cropped figure images
    - Store crop paths for downstream processing

    The extracted images are later used by
    figure captioning models.
    """

    def __init__(self, config):
        """
        Initialize configuration and create the
        figure debugging directory.
        """

        self.config = config

        os.makedirs(
            config["figure_debug_dir"],
            exist_ok=True
        )

        # Document Data Mapping
        self.mapper = Mapping(config)


    def save_crop_for_inspection(self, crop):
        """
        Save a cropped figure image.

        Persisting figure crops makes debugging
        and visual validation easier.
        """

        output_path = os.path.join(
            self.config["figure_debug_dir"],
            f"{uuid4()}.png"
        )

        cv2.imwrite(output_path, crop)

        return output_path


    def extract(self, element, page):
        """
        Extract a figure crop from a rendered page.

        The resulting crop is saved to disk and
        returned for downstream processing.
        """

        page_image = cv2.imread(page.image_path)

        if page_image is None:
            return None

        height, width = page_image.shape[:2]

        x1, y1, x2, y2 = map(int, element.bbox)

        # Clamp coordinates to image boundaries.
        x1 = max(0, min(x1, width))
        x2 = max(0, min(x2, width))

        y1 = max(0, min(y1, height))
        y2 = max(0, min(y2, height))

        crop = page_image[y1:y2, x1:x2]

        # Ignore invalid crops.
        if crop.size == 0:
            return None

        crop_path = self.save_crop_for_inspection(crop)

        # Store crop path for later
        # figure-captioning stages.
        element.metadata["figure_crop_path"] = crop_path

        return crop_path


    def process(self, document):
        """
        Extract crops for all detected figure
        elements in the document.
        """

        figure_crop_paths = []

        for element in document.elements:

            if element.element_type != "figure":
                continue

            page = document.get_page(element.page_number)

            crop_path = self.extract(element, page)

            # Store extracted figure image.
            if crop_path:
                element.image_path = crop_path

                figure_crop_paths.append(crop_path)
        
        if figure_crop_paths:
            self.mapper.add_document_data(
                document.document_id, 
                { "figure_crop_paths": figure_crop_paths }
            )

        return document