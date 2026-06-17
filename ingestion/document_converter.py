import os
import subprocess


class DocumentConverter:
    """
    Converts office documents into PDF format.

    Supported formats typically include:
    - DOCX
    - DOC
    - PPTX
    - PPT
    - ODT
    - ODP

    PDF is used as the canonical format for downstream
    processing because it provides a consistent structure
    for rendering, OCR, and layout analysis.
    """

    def __init__(self, converted_documents_dir):
        """
        Initialize the output directory where converted
        PDF files will be stored.
        """

        self.converted_documents_dir = converted_documents_dir


    def convert_to_pdf(self, file_path):
        """
        Convert a document into PDF using LibreOffice.

        Args:
            file_path:
                Path to the source document.

        Returns:
            str:
                Path to the generated PDF.

        Raises:
            FileNotFoundError:
                If the source file does not exist.

            RuntimeError:
                If conversion fails or the PDF
                cannot be located afterwards.
        """

        # Ensure the source file exists.
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        file_name = os.path.basename(file_path)

        output_dir = self.converted_documents_dir

        # Create output directory if needed.
        os.makedirs(output_dir, exist_ok=True)

        try:

            # Run LibreOffice in headless mode to
            # convert the document into PDF.
            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    file_path,
                    "--outdir",
                    output_dir
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Expected PDF output path.
            pdf_name = (
                os.path.splitext(file_name)[0]
                + ".pdf"
            )

            pdf_path = os.path.join(
                output_dir,
                pdf_name
            )

            # Verify that the conversion actually
            # produced a PDF file.
            if not os.path.exists(pdf_path):

                raise RuntimeError(
                    "PDF conversion succeeded "
                    "but output file was not found."
                )

            return pdf_path

        except subprocess.CalledProcessError as e:

            # Surface LibreOffice error messages
            # to the caller.
            raise RuntimeError(
                "Failed to convert document to PDF: "
                f"{e.stderr.decode(errors='ignore')}"
            )