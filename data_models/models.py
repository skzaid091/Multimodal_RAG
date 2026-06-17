from dataclasses import dataclass, field
from typing import List, Optional


# ==========================================================
# Table Structures
# ==========================================================

@dataclass
class TableCell:
    """
    Represents a single detected table cell.
    """

    row_index: int
    column_index: int

    bbox: list[float]

    colspan: int = 1

    text: str = ""


@dataclass
class TableData:
    """
    Structured representation of an extracted table.
    """

    image_path: str

    headers: list[str] = field(default_factory=list)

    rows: list[list[str]] = field(default_factory=list)

    title: str | None = None

    row_count: int = 0
    column_count: int = 0


# ==========================================================
# Figure Structures
# ==========================================================

@dataclass
class FigureData:
    """
    Information extracted from a figure or image.
    """

    caption: str = ""
    summary: str = ""

    figure_type: str = ""
    image_path: str | None = None

    error: str | None = None


# ==========================================================
# Page Structures
# ==========================================================

@dataclass
class PageContent:
    """
    Represents a single page within a document.
    Stores page text, dimensions, rendered image path,
    and OCR-related information.
    """

    page_number: int

    original_width: float
    original_height: float

    rendered_width: Optional[float] = None
    rendered_height: Optional[float] = None

    has_text_layer: bool = False
    text_blocks: list = field(default_factory=list)

    image_path: Optional[str] = None


# ==========================================================
# Layout Structures
# ==========================================================

@dataclass
class DocumentElement:
    """
    Generic layout element detected on a page.

    Examples:
    - title
    - text
    - table
    - figure
    - header
    - footer
    """

    page_number: int

    element_type: str

    confidence: float

    bbox: Optional[list] = None

    text: Optional[str] = None

    image_path: Optional[str] = None

    table_data: Optional[TableData] = None

    figure_data: Optional[FigureData] = None

    metadata: Optional[dict] = None


# ==========================================================
# Chunking Structures
# ==========================================================

@dataclass
class DocumentChunk:

    document_id: str

    chunk_id: str

    chunk_type: str

    chunk_index: int

    section_title: str

    page_number: int

    content: str

    metadata: dict = field(default_factory=dict)


@dataclass
class EmbeddingRecord:
    """
    Stores a chunk together with its vector embedding.
    Used for indexing in vector databases.
    """

    chunk_id: str

    text: str

    embedding: list[float]

    metadata: dict


# ==========================================================
# Document Structure
# ==========================================================

@dataclass
class Document:
    """
    Root object representing an ingested document.

    Every loader should return a Document instance so
    downstream pipeline components remain format-agnostic.
    """

    document_id: str
    
    source_type: str
    document_type: str

    original_file_path: str
    processed_file_path: str

    file_name: str

    page_count: int

    pages: List[PageContent]

    metadata: dict

    chunks: List[DocumentChunk] = field(
        default_factory=list
    )

    has_text_layer: Optional[bool] = False

    elements: List[DocumentElement] = field(
        default_factory=list
    )

    layout_metadata: dict = field(
        default_factory=dict
    )

    error: Optional[str] = None

    def get_page(self, page_number: int):
        """
        Retrieve a page using 1-based indexing.
        """
        return self.pages[page_number - 1]