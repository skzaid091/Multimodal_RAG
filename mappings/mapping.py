import os
import json
import shutil

from embeddings.chroma_store import ChromaStore
from embeddings.bm25_store import BM25Store


class Mapping:
    """
    Maintains mappings between document names and document IDs.

    Responsible for:
    - Document ID <-> Document Name mapping
    - Document metadata storage
    - Vector store cleanup
    - BM25 index cleanup
    - Generated file cleanup
    """

    def __init__(self, config):
        self.config = config

        # Storage backends
        self.chroma_store = ChromaStore(config)
        self.bm25_store = BM25Store(config)


    def get_file(self, path):
        """
        Load JSON data from the given file.

        Returns an empty dictionary if the file does not exist.
        """

        data = {}

        if os.path.exists(path):
            with open(path, "r") as file:
                data = json.load(file)

        return data


    def save_file(self, data, path):
        """
        Save dictionary data as a JSON file.
        """

        with open(path, "w") as file:
            json.dump(data, file, indent=4)


    def add_document_id_mapping(self, filename, document_id, document_data):
        """
        Create document mappings.

        Stores:
            document_id -> {
                filename,
                document_data
            }

            filename -> document_id
        """

        # Store document metadata against document ID
        data = self.get_file(self.config["document_id_mapping_file"])

        data.update({
            document_id: {
                "filename": filename,
                "document_data": document_data, 
                "document_info": {}
            }
        })

        self.save_file(data, self.config["document_id_mapping_file"])

        # Store reverse lookup
        data = self.get_file(self.config["document_name_mapping_file"])

        data.update({
            filename: document_id
        })

        self.save_file(data, self.config["document_name_mapping_file"])


    def add_document_data(self, document_id, document_data):
        """
        Update additional metadata for an existing document.
        """

        data = self.get_file(self.config["document_id_mapping_file"])

        data[document_id]["document_data"].update(document_data)

        self.save_file(data, self.config["document_id_mapping_file"])


    def add_document_info(self, document):
        """
        Extract and store document statistics.

        The stored information is used for displaying
        document summaries in the user interface and
        for knowledge base management operations.

        Stored statistics include:
        - Total pages
        - Total sections
        - Total chunks
        - Total figures
        - Total tables
        - Total formulas
        """

        document_id = document.document_id

        # --------------------------------------------------
        # Basic document statistics
        # --------------------------------------------------

        total_pages = len(document.pages)
        total_chunks = len(document.chunks)
        total_sections = len(document.sections)

        # --------------------------------------------------
        # Element statistics
        # --------------------------------------------------

        total_figures = sum(1 for chunk in document.chunks if chunk.chunk_type == "figure")
        total_tables = sum(1 for chunk in document.chunks if chunk.chunk_type == "table")
        total_formulas = sum(1 for chunk in document.chunks if chunk.chunk_type == "formula")

        # --------------------------------------------------
        # Build document metadata
        # --------------------------------------------------

        document_info = {
            "total_pages": total_pages,
            "total_chunks": total_chunks,
            "total_sections": total_sections,

            "total_figures": total_figures,
            "total_tables": total_tables,
            "total_formulas": total_formulas
        }

        # --------------------------------------------------
        # Update stored document information
        # --------------------------------------------------

        data = self.get_file(self.config["document_id_mapping_file"])

        data[document_id]["document_info"].update(document_info)

        # Persist changes
        self.save_file(data, self.config["document_id_mapping_file"])


    def get_documents(self):
        """
        Retrieve all document names currently
        available in the knowledge base.

        Returns:
            list:
                List of document names.
                Empty list if no documents exist.
        """

        data = self.get_file(
            self.config["document_name_mapping_file"]
        )

        return list(data.keys())


    def get_documents_info(self):
        """
        Retrieve information about all documents
        currently available in the knowledge base.

        Returns:
            list[dict]:
                Document summaries.

            None:
                If no documents exist.
        """

        data = self.get_file(self.config["document_id_mapping_file"])

        if not data:
            return None

        documents = []

        for document_id, document_data in data.items():

            documents.append(
                {
                    "document_id": document_id,
                    "document_name": document_data["filename"],
                    **document_data["document_info"]
                }
            )

        return documents


    def get_document_id(self, document_name):
        """
        Get document ID from document name.
        """

        data = self.get_file(self.config["document_name_mapping_file"])

        return data.get(document_name)


    def get_document_name(self, document_id):
        """
        Get document name from document ID.
        """

        data = self.get_file(self.config["document_id_mapping_file"])

        return data.get(document_id).get("filename")


    def delete_all_document_data(self):
        """
        Delete complete knowledge base.
        """

        for folder in self.config["reset_knowledge_base_folders"]:

            if not os.path.exists(folder):
                continue

            for item in os.listdir(folder):

                item_path = os.path.join(folder, item)

                if os.path.isfile(item_path):
                    os.remove(item_path)

                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

        return True, "Knowledge Base Reset Successfully. !!!"


    def delete_document_data(self, document_name=None, document_id=None):
        """
        Delete all resources associated with a document.

        Removes:
        - ChromaDB vectors
        - BM25 entries
        - Generated files
        - Mapping references
        """

        if not document_id and not document_name:
            return False, "Please provide Document, !!!"

        try:

            # Resolve document ID if only name is provided
            if not document_id:
                document_id = self.get_document_id(document_name)

            # Remove document from retrieval stores
            self.chroma_store.delete_document(document_id)

            self.bm25_store.delete_document(document_id)

            # Retrieve stored document metadata
            data = self.get_file(self.config["document_id_mapping_file"])

            document_data = data.get(document_id).get("document_data")

            # Remove generated files
            to_remove_paths = []
            for field, paths in document_data.items():
                if isinstance(paths, list):
                    to_remove_paths.extend(paths)
                    continue
                to_remove_paths.append(paths)

            for path in to_remove_paths:
                if os.path.exists(path):
                    os.remove(path)
                    print(f"{path} - removed")

            # Remove document mappings
            self.remove_document_references(document_id)

            return True, "Document Data Deleted. !!!"

        except:
            return False, "Document Deletion Failed. !!!"


    def remove_document_references(self, document_id):
        """
        Remove document mappings from both lookup files.
        """

        # Remove document_id -> metadata mapping
        data = self.get_file(self.config["document_id_mapping_file"])

        document_name = data.pop(document_id).get("filename")

        self.save_file(data, self.config["document_id_mapping_file"])

        # Remove document_name -> document_id mapping
        data = self.get_file(self.config["document_name_mapping_file"])

        data.pop(document_name)

        self.save_file(data, self.config["document_name_mapping_file"])
    

    def has_documents(self):
        """
        Check whether the knowledge base
        contains any indexed documents.
        """

        data = self.get_file(
            self.config["document_id_mapping_file"]
        )

        return len(data) > 0