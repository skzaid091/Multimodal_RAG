import re
import json


class TableLLMCorrector:
    """
    Improve OCR-derived table content using an LLM.

    OCR engines often introduce spelling mistakes
    in table headers and textual cells:

        Reglon  -> Region
        Departmant -> Department

    This stage runs after table reconstruction,
    when table content is available as structured
    rows rather than individual OCR cells.

    Numeric values, dates, identifiers, and table
    structure must remain unchanged.
    """

    def __init__(self, config, llm_service):

        self.config = config
        self.llm_service = llm_service

    

    def extract_json(self, response):

        if not response:
            raise ValueError("Empty response received.")

        response = response.strip()

        try:
            return json.loads(response)

        except Exception:
            pass

        # JSON Array
        match = re.search(r"\[.*\]", response, re.DOTALL)

        if match:
            return json.loads(match.group())

        # JSON Object
        match = re.search(r"\{.*\}", response, re.DOTALL)

        if match:
            return json.loads(match.group())

        raise ValueError(f"No JSON found:\n{response}")
    

    def _correct_tables(self, table_elements):
        """
        Correct OCR mistakes across multiple tables
        using a single batched LLM request.

        Each table is assigned an identifier so
        corrected results can be mapped back to
        the originating table.
        """

        payload = []

        # Build a lightweight representation of
        # table content for the LLM.
        for idx, element in enumerate(table_elements):

            payload.append(
                {
                    "id": idx,
                    "rows": element.table_data.rows
                }
            )

        prompt = f"""Correct only obvious OCR spelling mistakes.

        Rules:

        - Do not modify numbers.
        - Do not modify dates.
        - Do not modify currency values.
        - Do not modify IDs.
        - Do not add rows.
        - Do not remove rows.
        - Do not reorder rows.
        - Do not reorder columns.

        Only fix obvious OCR spelling mistakes.

        Return ONLY valid JSON.
        Do not wrap the JSON in markdown.
        Do not add explanations.

        - If you are uncertain whether a value is an OCR mistake, leave it unchanged.

        Input:

        {json.dumps(payload, indent=2)}
        """

        response = self.llm_service.invoke(
            prompt=prompt,
            temperature=0
        )

        corrected = self.extract_json(response)
        # corrected = json.loads(response)

        # Update table content using the corrected
        # rows returned by the model.
        for item in corrected:

            table = table_elements[item["id"]]

            table.table_data.rows = item["rows"]


    def process(self, document):
        """
        Apply OCR correction to all extracted
        tables within the document.

        Workflow:

            Extracted TableData
                    ↓
            Batch LLM Correction
                    ↓
            Corrected TableData
        """

        table_elements = []

        for element in document.elements:

            # Process only tables that have already
            # been reconstructed into TableData.
            if element.element_type == "table" and element.table_data:
                table_elements.append(element)

        # Skip processing when no tables exist.
        if not table_elements:
            return document

        # Correct all tables in a single batch to
        # reduce API calls and improve efficiency.
        self._correct_tables(table_elements)

        return document