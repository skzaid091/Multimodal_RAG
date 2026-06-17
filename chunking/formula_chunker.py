from uuid import uuid4

from data_models.models import DocumentChunk


class FormulaChunker:
    """
    Build retrievable chunks from formulas.

    Responsibilities:
    - Convert formulas into chunks.
    - Preserve section context.
    - Preserve page information.
    - Create a single chunk per formula.
    """

    def __init__(self, config):

        self.config = config

        self.formula_no = 1


    def process(self, element, section, document_id):
        """
        Create a chunk from a formula element.

        Parameters:
            element: Formula element.

            section: Parent section.

        Returns:
            List[DocumentChunk]
        """

        formula = (element.text or "").strip()

        if not formula:
            return []

        chunk = DocumentChunk(

            document_id=document_id,

            chunk_id=str(uuid4()).split("-")[-1],

            chunk_index=-1,

            chunk_type="formula",

            section_title=section["title"],

            page_number=element.page_number,

            content = (
                f"Formula Number: {self.formula_no}\n\n"
                f"Section: {section['title']}\n\n"
                f"Formula:\n{formula}"
            ),

            metadata={
                "formula_no": self.formula_no
            }
        )

        self.formula_no += 1

        return [chunk]