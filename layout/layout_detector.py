from doclayout_yolo import YOLOv10
from data_models.models import DocumentElement

from uuid import uuid4
from collections import Counter


class LayoutDetector:
    """
    Detects document layout elements using DocLayout-YOLO.

    Responsibilities:
    - Detect layout regions
    - Create DocumentElement objects
    - Remove duplicate detections
    - Sort elements in reading order
    - Generate layout statistics
    """

    def __init__(self, config):
        """
        Load the layout detection model.
        """

        self.config = config

        self.model = YOLOv10(
            config["layout_model_path"]
        )


    def _iou(self, box1, box2):
        """
        Compute Intersection over Union (IoU)
        between two bounding boxes.

        IoU is used to identify overlapping
        detections during duplicate removal.
        """

        x_left = max(box1[0], box2[0])
        y_top = max(box1[1], box2[1])

        x_right = min(box1[2], box2[2])
        y_bottom = min(box1[3], box2[3])

        if x_right <= x_left or y_bottom <= y_top:
            return 0.0

        intersection = (
            (x_right - x_left)
            * (y_bottom - y_top)
        )

        area1 = (
            (box1[2] - box1[0])
            * (box1[3] - box1[1])
        )

        area2 = (
            (box2[2] - box2[0])
            * (box2[3] - box2[1])
        )

        union = area1 + area2 - intersection

        if union <= 0:
            return 0.0

        return intersection / union


    def _remove_duplicates(self, elements):
        """
        Remove highly overlapping detections.

        For overlapping elements of the same type,
        the detection with the highest confidence
        score is retained.
        """

        filtered = []

        # Process highest-confidence detections first.
        elements = sorted(
            elements,
            key=lambda e: e.confidence,
            reverse=True
        )

        for current in elements:

            duplicate = False

            for kept in filtered:

                if (
                    current.page_number == kept.page_number
                    and current.element_type == kept.element_type
                    and self._iou(
                        current.bbox,
                        kept.bbox
                    ) > self.config["iou_threshold"]
                ):
                    duplicate = True
                    break

            if not duplicate:
                filtered.append(current)

        return filtered


    def _process_results(self, document, page, result):
        """
        Convert model predictions into
        DocumentElement objects.
        """

        names = result.names
        boxes = result.boxes

        for bbox, cls_id, conf in zip(
            boxes.xyxy.tolist(),
            boxes.cls.tolist(),
            boxes.conf.tolist()
        ):

            # Ignore low-confidence detections
            # and abandoned regions.
            if (conf < self.config["layout_confidence_threshold"] or names[int(cls_id)] == "abandon"):
                continue
            
            if "formula" in names[int(cls_id)]:
                element_type = "formula"
            else:
                element_type = names[int(cls_id)]
                
            document.elements.append(
                DocumentElement(
                    page_number=page.page_number,

                    element_type=element_type,
                    bbox=bbox,
                    confidence=float(conf),

                    metadata={}
                )
            )


    def process(self, document):
        """
        Run layout detection across all pages.

        Workflow:
        1. Detect layout elements.
        2. Remove duplicate detections.
        3. Sort elements in reading order.
        4. Generate layout statistics.
        """

        if document.error:
            return document

        for page in document.pages:

            results = self.model.predict(page.image_path, verbose=False)

            self._process_results(document, page, results[0])

        # Remove overlapping detections.
        document.elements = self._remove_duplicates(document.elements)

        # Sort elements in reading order:
        # page -> top -> left
        document.elements.sort(
            key=lambda element: (
                element.page_number,
                element.bbox[1],
                element.bbox[0]
            )
        )

        # Generate summary statistics.
        document.layout_metadata = {
            "total_elements": len(document.elements),
            "element_counts": dict(
                Counter(
                    e.element_type
                    for e in document.elements
                )
            )
        }

        return document