from mappings.mapping import Mapping


class CitationBuilder:
    """
    Builds structured citations from retrieved chunks.

    Groups chunks by document and collects:
    - Referenced pages
    - Referenced sections
    - Referenced figures
    - Referenced tables
    - Referenced equations
    """

    def __init__(self, config):

        self.config = config

        # Document ID <-> Document Name resolver
        self.mapper = Mapping(config)


    def build(self, chunks):
        """
        Generate citation metadata for the retrieved chunks.

        Returns:
            list[dict]:
                Citation information grouped by document.
        """

        sources = {}

        for chunk in chunks:

            # Resolve document name from document ID
            document_name = self.mapper.get_document_name(
                chunk["document_id"]
            )

            # Create source entry if document
            # has not been processed yet
            if document_name not in sources:

                sources[document_name] = {
                    "document_name": document_name,

                    # Use sets to avoid duplicates
                    "pages": set(),
                    "referenced_sections": set(),

                    "referenced_figures": [],
                    "referenced_tables": [],
                    "referenced_equations": []
                }

            source = sources[document_name]

            # --------------------------------------------------
            # Pages
            # --------------------------------------------------
            if chunk["page_number"] is not None:
                source["pages"].add(chunk["page_number"])

            # --------------------------------------------------
            # Sections
            # --------------------------------------------------
            if chunk["section_title"]:
                source["referenced_sections"].add(chunk["section_title"])

            # --------------------------------------------------
            # Figures
            # --------------------------------------------------
            if chunk["chunk_type"] == "figure":

                figure_no = chunk["metadata"].get("figure_no")

                if figure_no is not None:

                    figure = {
                        "figure_no": figure_no,
                        "page_number": chunk["page_number"],
                        "crop_path": (
                            chunk["metadata"]
                            .get("crop_path")
                        )
                    }

                    # Prevent duplicate figure references
                    if figure not in source["referenced_figures"]:
                        source["referenced_figures"].append(figure)

            # --------------------------------------------------
            # Tables
            # --------------------------------------------------

            elif chunk["chunk_type"] == "table":

                table_no = chunk["metadata"].get("table_no")

                if table_no is not None:

                    table = {
                        "table_no": table_no,
                        "page_number": chunk["page_number"],
                        "crop_path": (
                            chunk["metadata"]
                            .get("crop_path")
                        )
                    }

                    # Prevent duplicate table references
                    if table not in source["referenced_tables"]:
                        source["referenced_tables"].append(table)

            # --------------------------------------------------
            # Equations
            # --------------------------------------------------

            elif chunk["chunk_type"] == "formula":

                equation_no = chunk["metadata"].get("formula_no")

                if equation_no is not None:

                    equation = {
                        "equation_no": equation_no,
                        "page_number": chunk["page_number"]
                    }

                    # Prevent duplicate equation references
                    if equation not in source["referenced_equations"]:
                        source["referenced_equations"].append(equation)

        # --------------------------------------------------
        # Convert sets to sorted lists
        # --------------------------------------------------

        for source in sources.values():

            source["pages"] = sorted(source["pages"])
            source["referenced_sections"] = sorted(source["referenced_sections"])

        return list(sources.values())