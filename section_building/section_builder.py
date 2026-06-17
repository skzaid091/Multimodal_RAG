class SectionBuilder:

    """
    Groups document elements into
    logical sections.

    Example:

        Title
            Paragraph
            Paragraph

        Title
            Paragraph

    becomes

        document.sections
    """

    def process(self, document):

        sections = []
        current_section = None

        for element in document.elements:

            # -------------------------
            # Start new section
            # -------------------------

            if element.element_type == "title":

                if current_section:
                    sections.append(current_section)

                current_section = {
                    "title": element.text, 
                    "elements": []
                }

                continue

            # -------------------------
            # Content before title
            # -------------------------

            if current_section is None:

                current_section = {
                    "title": "Untitled Section",
                    "elements": []
                }

            current_section["elements"].append(element)

        # -------------------------
        # Save last section
        # -------------------------

        if current_section:
            sections.append(current_section)

        document.sections = sections

        return document