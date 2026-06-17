# ============================================================
# Libraries
# ============================================================

import os

# ============================================================
# Configuration
# ============================================================
from configurations.config_manager import ConfigManager

# ============================================================
# Core Services
# ============================================================
from language_models.llm_service import LLMService
from language_models.vlm_service import VLM_Service

# ============================================================
# Document Ingestion
# ============================================================
from ingestion.loader import DocumentLoader

from layout.layout_detector import LayoutDetector

from extraction.text_extractor import TextExtractor
from extraction.table.table_extractor import TableExtractor
from extraction.figure.figure_extractor import FigureExtractor

from cleaner.element_cleaner import ElementCleaner
from document_post_processing.document_cleaner import DocumentCleaner

from section_building.section_builder import SectionBuilder
from chunking.chunk_builder import ChunkBuilder

from embeddings.embedding_generator import EmbeddingGenerator

# ============================================================
# Query Processing
# ============================================================
from query_rewriting.query_rewriter import QueryRewriter

# ============================================================
# Retrieval-Augmented Generation (RAG)
# ============================================================
from retrieval.retriever import Retriever
from reranking.reranker import Reranker
from context_building.context_builder import ContextBuilder
from generation.generator import Generator

# ============================================================
# Knowledge Base Management
# ============================================================
from mappings.mapping import Mapping



class MultimodalRAG:

    def __init__(self, GROQ_API_KEY=None):

        # ============================================================
        # Configuration
        # ============================================================

        self.config_manager = ConfigManager(settings_file="configurations/settings.json")
        self.config = self.config_manager.load()

        # ============================================================
        # Shared Services
        # ============================================================

        self.llm_service = LLMService(self.config["llm_model"], GROQ_API_KEY)
        self.vlm_service = VLM_Service(self.config["vlm_model"], GROQ_API_KEY)

        # ============================================================
        # Document Ingestion Pipeline
        # ============================================================

        # Load document from disk
        self.loader = DocumentLoader(self.config)

        # Detect document layout elements
        self.layout_detector = LayoutDetector(self.config)

        # Extract OCR/text content
        self.text_extractor = TextExtractor(
            self.config,
            self.llm_service
        )

        # Clean extracted elements
        self.element_cleaner = ElementCleaner(self.config)

        # Extract structured content
        self.table_extractor = TableExtractor(
            self.config,
            self.llm_service
        )
        self.figure_extractor = FigureExtractor(self.config, self.vlm_service)

        # Document-level cleanup
        self.document_cleaner = DocumentCleaner(self.config)

        # Build document hierarchy
        self.section_builder = SectionBuilder()

        # Convert sections into chunks
        self.chunker = ChunkBuilder(self.config)

        # Generate vector embeddings
        self.embedding_generator = EmbeddingGenerator(
            self.config
        )

        # ============================================================
        # Retrieval Pipeline
        # ============================================================

        self.query_rewriter = QueryRewriter(
            self.llm_service
        )

        self.retriever = Retriever(self.config)

        self.reranker = Reranker(self.config)

        self.context_builder = ContextBuilder(
            self.config
        )

        self.generator = Generator(self.config, self.llm_service)

        # ============================================================
        # Knowledge Base Metadata
        # ============================================================

        self.mapper = Mapping(self.config)




    # ============================================================
    # Configuration Management
    # ============================================================

    def reload_config(self):
        """
        Reload configuration from disk.
        """

        self.config = self.config_manager.load()


    def get_config(self):
        """
        Return the current runtime configuration.
        """

        return self.config


    def update_config(self, updates):
        """
        Update configuration values and
        persist them to disk.
        """

        self.config.update(updates)
        self.config_manager.save(self.config)


    def reset_config(self):
        """
        Restore the default configuration
        and reload it into memory.
        """

        self.config_manager.reset()

        self.config.clear()

        self.config.update(self.config_manager.load())





    def process_document(self, document_path):

        # ========================================================
        # Load Document
        # ========================================================

        document = self.loader.load(document_path)

        if document.error:
            return document

        # ========================================================
        # Extraction Pipeline
        # ========================================================

        document = self.layout_detector.process(document)

        document = self.text_extractor.process(document)

        document = self.element_cleaner.process(document)

        document = self.table_extractor.process(document)

        document = self.figure_extractor.process(document)

        document = self.document_cleaner.process(document)

        # ========================================================
        # Structure Building
        # ========================================================

        document = self.section_builder.process(document)

        document = self.chunker.process(document)

        # ========================================================
        # Embedding Generation
        # ========================================================

        self.embedding_generator.process(document)

        # ========================================================
        # Metadata Registration
        # ========================================================

        self.mapper.add_document_info(document)

        return "Document added to Knowledge Base !!!"




    # ============================================================
    # Query Processing
    # ============================================================

    def modify_query(self, query):
        """
        Rewrite the query using conversation
        history when query rewriting is enabled.
        """

        if self.config["enable_query_rewriting"]:

            history = self.context_builder.build_history_context()

            return self.query_rewriter.rewrite(
                history,
                query
            )

        return query
    



    # ============================================================
    # Retrieval-Augmented Generation (RAG)
    # ============================================================

    def ask(self, query):

        # ========================================================
        # Knowledge Base Validation
        # ========================================================

        if not self.mapper.has_documents:
            return {
                "answer": (
                    "The knowledge base is empty. "
                    "Please upload and process at least one document first."
                ),
                "citations": []
            }

        # ========================================================
        # Query Rewriting
        # ========================================================

        query = self.modify_query(query)

        # ========================================================
        # Retrieval
        # ========================================================

        chunks = self.retriever.retrieve(
            query, 
            top_k=self.config["retrieval_k"]
        )

        # ========================================================
        # Reranking
        # ========================================================

        chunks = self.reranker.rerank(
            query, chunks, 
            top_k=self.config["reranking_k"]
        )

        # ========================================================
        # Context Construction
        # ========================================================

        context = self.context_builder.build(
            query, chunks,
            query_rewriting=self.config["enable_query_rewriting"]
        )

        # ========================================================
        # Answer Generation
        # ========================================================

        response = self.generator.generate(
            context,
            chunks
        )

        # ========================================================
        # Conversation Memory
        # ========================================================

        self.context_builder.update_memory(
            query,
            response["answer"]
        )

        return response
    



    # ============================================================
    # Knowledge Base Management
    # ============================================================

    def process_multiple_documents(self, documents):
        """
        Process and index multiple documents.

        Args:
            documents (List[str]): List of document paths.

        Returns:
            str: Processing status message.
        """

        for document in documents:
            self.process_document(document)

        return "All documents processed !!!"


    def delete_document(self, document_name):
        """
        Remove a document and all associated
        chunks, embeddings, and metadata from
        the knowledge base.
        """

        self.mapper.delete_document_data(
            document_name=document_name
        )


    def reset_knowledge_base(self):
        """
        Completely remove all indexed documents,
        embeddings, metadata, and mappings.
        """

        self.mapper.delete_all_document_data()




    # ============================================================
    # Conversation Memory Management
    # ============================================================

    def clear_history(self):
        """
        Clear conversation history used for
        query rewriting and conversational
        retrieval.
        """

        self.context_builder.clear_memory()


    def update_memory_conf_and_history(self, new_max_history):
        """
        Update the maximum conversation history
        size and trim existing memory if needed.

        Args:
            new_max_history (int): Maximum number
            of conversation turns to retain.
        """

        self.context_builder.update_memory_conf_and_history(
            new_max_history
        )