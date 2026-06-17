import os
from dotenv import load_dotenv

load_dotenv()

"""
Application Configuration

This file contains all configurable parameters used throughout the
Multimodal RAG / Document Understanding System.
"""

DEFAULT_CONFIG = {

    # ==========================================================
    # Mapping Files
    # ==========================================================

    # Document ID -> Metadata mapping
    "document_id_mapping_file":
        "data/mappings/document_id_mapping.json",

    # Document Name -> Document ID mapping
    "document_name_mapping_file":
        "data/mappings/document_name_mapping.json",

    # ==========================================================
    # Directory Paths
    # ==========================================================

    # Raw uploaded documents
    "raw_documents_dir":
        "data/raw_documents",

    # Converted PDF documents
    "converted_documents_dir":
        "data/converted_documents",

    # Final processed documents
    "processed_documents_dir":
        "data/converted_documents",

    # Rendered page images
    "document_images_dir":
        "data/documents_images",

    # Table extraction debugging outputs
    "table_debug_dir":
        "data/table_debugging",

    # Figure extraction debugging outputs
    "figure_debug_dir":
        "data/figure_debugging",

    # Chunk storage
    "chunk_storage_path":
        "data/chunk_data",

    # ==========================================================
    # Supported File Types
    # ==========================================================

    # Office files requiring PDF conversion
    "CONVERTIBLE_TYPES": [
        ".docx",
        ".doc",
        ".pptx",
        ".ppt",
        ".odt",
        ".odp"
    ],

    # Image formats
    "IMAGE_TYPES": [
        ".png",
        ".jpg",
        ".jpeg"
    ],

    # Spreadsheet formats
    "EXCEL_TYPES": [
        ".xlsx",
        ".xls",
        ".ods"
    ],

    # CSV formats
    "CSV_TYPES": [
        ".csv"
    ],

    # ==========================================================
    # PDF Processing
    # ==========================================================

    # Resolution used when rendering pages
    "pdf_render_dpi": 300,

    # ==========================================================
    # OCR Configuration
    # ==========================================================

    # OCR engine
    "ocr_type": "EasyOCR",

    # OCR language
    "ocr_language": "en",

    # Enable text angle classification
    "ocr_use_angle_cls": True,

    # Correct OCR mistakes using LLM
    "enable_ocr_correction": True,

    # ==========================================================
    # Layout Detection
    # ==========================================================

    # Layout detection backend
    "layout_model": "doclayout-yolo",

    # Layout model path
    "layout_model_path":
        "models/layout/doclayout_yolo_ft.pt",

    # Minimum prediction confidence
    "layout_confidence_threshold": 0.25,

    # IoU threshold for element matching
    "iou_threshold": 0.6,

    # ==========================================================
    # Document Element Processing
    # ==========================================================

    # Layout classes treated as textual content
    "TEXT_ELEMENT_TYPES": [

        "plain text",
        "title",
        "header",
        "footer",

        "figure_caption",
        "table_caption",
        "formula_caption",

        "formula",
        "isolate_formula"
    ],

    # Elements requiring LLM descriptions
    "generate_element_description": [
        "formula",
        "isolate_formula"
    ],

    # ==========================================================
    # Figure Understanding
    # ==========================================================

    # Vision-Language Model
    "vlm_model":
        "meta-llama/llama-4-scout-17b-16e-instruct",

    # ==========================================================
    # Embeddings & Retrieval Models
    # ==========================================================

    # Embedding model
    "embedding_model_path":
        "models/embeddings/bge-base-en-v1.5",

    # Cross-encoder reranker
    "reranker_model_path":
        "models/rerankers/bge-reranker-base",

    # Response generation LLM
    "llm_model":
        "llama-3.3-70b-versatile",

    # ==========================================================
    # Vector Storage
    # ==========================================================

    # ChromaDB persistence directory
    "chroma_db_path":
        "data/embedding_storage/chroma",

    # BM25 index file
    "bm25_index_path":
        "data/embedding_storage/bm25/bm25_index.json",

    # Chroma collection name
    "collection_name":
        "documents",

    # ==========================================================
    # Chunking
    # ==========================================================

    "chunking": {

        # Desired chunk size
        "target_chunk_size": 200,

        # Minimum acceptable chunk size
        "min_chunk_size": 100,

        # Overlap between adjacent chunks
        "overlap_size": 20
    },

    # ==========================================================
    # Retrieval Configuration
    # ==========================================================

    # dense | sparse | hybrid
    "retrieval_type": "dense",

    # Initial retrieval count
    "retrieval_k": 10,

    # Final reranked count
    "reranking_k": 7,

    # Maximum chunks used in context
    "context_max_chunks": 7,

    # Response Mode (precise | detailed)
    "response_mode": "precise",

    # ==========================================================
    # Conversation Memory
    # ==========================================================

    # Number of previous interactions retained
    "conversation_max_history": 5,

    # Enable query rewriting using conversation history
    "enable_query_rewriting": True,

    # ==========================================================
    # Knowledge Base Management
    # ==========================================================

    # Folders cleared during reset operation
    "reset_knowledge_base_folders": [

        "data/chunk_data",

        "data/mappings",

        "data/raw_documents",

        "data/converted_documents",

        "data/documents_images",

        "data/table_debugging",

        "data/figure_debugging",

        "data/embedding_storage"
    ]
}