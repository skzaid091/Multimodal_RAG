from .table_cell_generator import TableCellGenerator
from .table_structure_processor import TableStructureProcessor


from transformers import (
    AutoImageProcessor,
    TableTransformerForObjectDetection
)

from PIL import Image
import torch



class TATRExtractor:
    """
    Extracts table structure using Microsoft's
    Table Transformer (TATR).

    Responsibilities:
    - Detect rows and columns
    - Detect header regions
    - Detect spanning cells
    - Post-process structure predictions
    - Generate table cell grid

    This component transforms a table image into a
    structured representation that can later be
    populated with OCR text.
    """

    def __init__(self, config):
        """
        Load the Table Transformer model and
        supporting post-processing components.
        """

        self.config = config

        self.processor = (
            AutoImageProcessor
            .from_pretrained(
                "microsoft/table-transformer-structure-recognition"
            )
        )

        self.model = (
            TableTransformerForObjectDetection
            .from_pretrained(
                "microsoft/table-transformer-structure-recognition"
            )
        )

        # Generates cell grid from detected rows
        # and columns.
        self.cell_generator = TableCellGenerator()

        # Performs additional structure cleanup.
        self.table_structure_processor = TableStructureProcessor(config)


    def extract_structure(self, crop_path):
        """
        Detect table structure from a cropped
        table image.

        Returns:
            structure dictionary containing:
            - table_bbox
            - rows
            - columns
            - column_headers
            - projected_row_headers
            - spanning_cells
        """

        image = Image.open(crop_path).convert("RGB")

        inputs = self.processor(images=image, return_tensors="pt")

        # Run inference.
        with torch.no_grad():
            outputs = self.model(**inputs)

        target_sizes = torch.tensor([image.size[::-1]])

        # Convert model outputs into bounding boxes.
        results = (
            self.processor
            .post_process_object_detection(
                outputs,
                threshold=0.7,
                target_sizes=target_sizes
            )[0]
        )

        structure = {
            "table_bbox": None,
            "rows": [],
            "columns": [],
            "column_headers": [],
            "projected_row_headers": [],
            "spanning_cells": []
        }

        # Parse TATR detections.
        for _, label, box in zip( results["scores"], results["labels"], results["boxes"]):

            label_name = (
                self.model.config.id2label[
                    label.item()
                ]
            )

            bbox = box.tolist()

            if label_name == "table":
                structure["table_bbox"] = bbox

            elif label_name == "table row":
                structure["rows"].append(bbox)

            elif label_name == "table column":
                structure["columns"].append(bbox)

            elif (label_name == "table column header"):
                structure["column_headers"].append(bbox)

            elif (label_name == "table projected row header"):
                structure["projected_row_headers"].append(bbox)

            elif (label_name == "table spanning cell"):
                structure["spanning_cells"].append(bbox)

        # Preserve visual ordering.
        structure["rows"].sort(key=lambda row: row[1])

        structure["columns"].sort(key=lambda column: column[0])

        return structure


    def process(self, document):
        """
        Run table structure extraction on all
        detected table elements.
        """

        for element in document.elements:

            if element.element_type != "table":
                continue

            crop_path = element.metadata.get("table_crop_path")

            if not crop_path:
                continue

            # Detect table structure.
            structure = self.extract_structure(crop_path)

            # Post-process structure predictions.
            structure = self.table_structure_processor.process(structure)

            # Generate logical table cells.
            cells = self.cell_generator.generate(structure)

            # Store extracted structure.
            element.metadata["table_structure"] = structure

            element.metadata["table_cells"] = cells

        return document