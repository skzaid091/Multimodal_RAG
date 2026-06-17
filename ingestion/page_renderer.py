import os
import pymupdf


class PageRenderer:
    """
    Renders PDF pages into image files.

    Rendering serves as the foundation for downstream
    vision-based processing such as:

    - OCR
    - Layout Detection
    - Table Extraction
    - Figure Analysis
    - Vision-Language Models

    The rendered image paths are stored directly inside
    the corresponding PageContent objects.
    """

    def __init__(self, config):
        """
        Store application configuration.
        """

        self.config = config


    def render(self, document, mapper):
        """
        Render document pages into images.

        If the document already contains an error,
        rendering is skipped.
        """

        if document.error:
            return document

        return self._render_pdf(document, mapper)


    def _render_pdf(self, document, mapper):
        """
        Render every PDF page as a PNG image and update
        the corresponding PageContent metadata.

        Updates:
        - image_path
        - rendered_width
        - rendered_height
        """

        document_name = os.path.splitext(document.file_name)[0]

        output_dir = os.path.join(
            self.config["document_images_dir"],
            document_name
        )

        # Create output directory for rendered pages.
        os.makedirs(output_dir, exist_ok=True)

        # Target rendering resolution.
        dpi = self.config["pdf_render_dpi"]

        # PDF coordinates use a default resolution of 72 DPI.
        # Scaling by dpi / 72 produces the requested render size.
        zoom = dpi / 72

        matrix = pymupdf.Matrix(zoom, zoom)

        with pymupdf.open(document.processed_file_path) as pdf:

            for page in pdf:

                image_path = os.path.join(output_dir, f"page_{page.number + 1}.png")

                # Render page into a raster image.
                pixmap = page.get_pixmap(matrix=matrix)

                pixmap.save(image_path)

                # Update the corresponding page object
                # with rendering information.
                document.pages[page.number].image_path = image_path

                document.pages[page.number].rendered_width = pixmap.width

                document.pages[page.number].rendered_height = pixmap.height
        

        mapper.add_document_id_mapping(
            document.file_name, 
            document.document_id, 
            document_data={"document_pages_dir": output_dir}
        )

        return document