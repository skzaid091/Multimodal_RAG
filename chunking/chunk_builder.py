import os
import json
from dataclasses import asdict

from .text_chunker import TextChunker
from .table_chunker import TableChunker
from .figure_chunker import FigureChunker
from .formula_chunker import FormulaChunker

from mappings.mapping import Mapping


class ChunkBuilder:
    """
    Build all chunk types for a document.

    Responsibilities:
    - Generate text chunks
    - Generate table chunks
    - Generate figure chunks
    - Generate formula chunks

    Produces a unified chunk collection
    for indexing and retrieval.
    """

    def __init__(self, config):

        self.config = config

        self.text_chunker = TextChunker(config)

        self.table_chunker = TableChunker(config)

        self.figure_chunker = FigureChunker(config)

        self.formula_chunker = FormulaChunker(config)

        self.mapper = Mapping(config)
    

    def process(self, document):

        chunks = []
        document_id = document.document_id

        for section in document.sections:

            for element in section["elements"]:

                if element.element_type == "plain text":
                    chunks.extend(
                        self.text_chunker.process(element, section, document_id)
                    )

                elif element.element_type == "table":

                    chunks.extend(self.text_chunker.flush(document_id))
                    chunks.extend(
                        self.table_chunker.process(element, section, document_id)
                    )

                elif element.element_type == "figure":
                    chunks.extend(self.text_chunker.flush(document_id))
                    chunks.extend(
                        self.figure_chunker.process(element, section, document_id)
                    )

                elif element.element_type in ["isolate_formula", "formula"]:
                    chunks.extend(self.text_chunker.flush(document_id))
                    chunks.extend(
                        self.formula_chunker.process(element, section, document_id)
                    )
            
        # Final flush for remaining text
        chunks.extend(
            self.text_chunker.flush(document_id)
        )

        document.chunks = chunks
        for index, chunk in enumerate(document.chunks):
            chunk.chunk_index = index
            
        self.save_chunks(document)

        return document
    

    def save_chunks(self, document):

        output_dir = self.config["chunk_storage_path"]

        os.makedirs(output_dir, exist_ok=True)

        file_path = os.path.join(output_dir, f"{document.document_id}.json")

        chunks = [asdict(chunk) for chunk in document.chunks]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=4)
        
        self.mapper.add_document_data(
            document.document_id, 
            { "chunks_data_file_path": file_path }
        )

        return file_path