from uuid import uuid4

from data_models.models import DocumentChunk


class TextChunker:
    """
    Build text chunks while preserving
    document reading order.

    Responsibilities:
    - Accumulate consecutive text elements
    - Create chunks using target size
    - Apply chunk overlap
    - Avoid tiny chunks
    - Preserve section context
    """

    def __init__(self, config):

        self.config = config

        chunking_config = config["chunking"]
        self.target_chunk_size =chunking_config["target_chunk_size"]
        self.min_chunk_size = chunking_config["min_chunk_size"]
        self.overlap_size = chunking_config["overlap_size"]

        self.current_text = []

        self.current_word_count = 0

        self.current_page_number = None

        self.current_section = None


    def process(self, element, section, document_id):
        """
        Process a text element.

        Returns:
            List[DocumentChunk]
        """

        emitted_chunks = []

        text = (element.text or "").strip()

        if not text:
            return emitted_chunks

        # Detect section change.
        if self.current_section is not section:

            emitted_chunks.extend(self.flush(document_id=document_id))

            self.current_section = (section)

        word_count = len(text.split())

        # First page entering chunk.
        if self.current_page_number is None:
            self.current_page_number = element.page_number

        # Emit current chunk before
        # exceeding target size.
        if (self.current_word_count + word_count > self.target_chunk_size):

            emitted_chunks.extend(self._emit_chunk(document_id=document_id))

            if self.current_page_number is None:
                self.current_page_number = element.page_number

        self.current_text.append(text)

        self.current_word_count += word_count

        return emitted_chunks


    def flush(self, document_id):
        """
        Flush pending text.

        Called when:
        - Figure appears
        - Table appears
        - Formula appears
        - Section ends

        Returns:
            List[DocumentChunk]
        """

        return self._emit_chunk(document_id=document_id, force=True)


    def _emit_chunk(self, document_id=None, force=False):
        """
        Create a chunk from the
        accumulated text.
        """

        if not self.current_text:
            return []

        content = "\n\n".join(self.current_text)

        word_count = len(content.split())

        # Avoid tiny chunks unless
        # explicitly forced.
        if (word_count < self.min_chunk_size and not force):
            return []

        chunk = DocumentChunk(
            
            document_id=document_id,
            
            chunk_id=str(uuid4()).split("-")[-1],

            chunk_index=-1,

            chunk_type="text",

            section_title=self.current_section["title"],

            page_number=self.current_page_number,

            content=content,

            metadata={
                "word_count": word_count
            }
        )

        overlap_text = self._get_overlap_text(content)

        if force:
            self.current_text = []
            self.current_word_count = 0

        elif overlap_text:
            self.current_text = [overlap_text]
            self.current_word_count = len(overlap_text.split())

        else:
            self.current_text = []
            self.current_word_count = 0

        self.current_page_number = None

        return [chunk]


    def _get_overlap_text(self, content):
        """
        Extract overlap words from
        the end of a chunk.
        """

        if self.overlap_size <= 0:
            return ""

        words = content.split()

        if len(words) <= self.overlap_size:
            return content

        overlap_words = words[-self.overlap_size:]

        return " ".join(overlap_words)