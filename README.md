# Multimodal Document Understanding & RAG System

A production-oriented **Multimodal Retrieval-Augmented Generation (RAG)** system that transforms unstructured documents into a searchable knowledge base and enables grounded question answering with source citations.

The system supports PDFs, images, scanned documents, tables, figures, spreadsheets, hybrid retrieval, query rewriting, reranking, and conversational memory.

---

## Features

### Document Processing
- PDF ingestion
- Image ingestion
- CSV ingestion
- Excel ingestion
- OCR support for scanned documents

### Content Understanding
- Layout detection
- Text extraction
- Table extraction
- Figure extraction
- Section building

### Retrieval Pipeline
- Dense retrieval
- BM25 retrieval
- Hybrid retrieval
- Reranking
- Query rewriting
- Conversation memory

### Answer Generation
- Citation-aware responses
- Grounded answer generation
- Multi-turn conversations

### Management
- Document management
- Knowledge base reset
- Runtime configuration controls
- Streamlit dashboard

---

## Architecture

```text
Document
    │
    ▼
Document Loader
    │
    ▼
Layout Detection
    │
    ▼
Content Extraction
 ├── Text
 ├── Tables
 └── Figures
    │
    ▼
Cleaning & Post Processing
    │
    ▼
Section Builder
    │
    ▼
Chunk Builder
    │
    ▼
Embedding Generation
    │
    ▼
Vector Store + BM25 Index
    │
    ▼
Hybrid Retrieval
    │
    ▼
Reranking
    │
    ▼
Context Building
    │
    ▼
Answer Generation
    │
    ▼
Citations
```

---

## Supported Document Types

| Format | Supported |
|----------|-----------|
| PDF | ✅ |
| PNG / JPG / JPEG | ✅ |
| CSV | ✅ |
| XLSX | ✅ |
| Scanned Documents | ✅ |
| Tables | ✅ |
| Figures | ✅ |

---

## Installation

### Clone the Repository

```bash
git clone <repository-url>
cd multimodal-document-understanding
```

### Create a Virtual Environment

#### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Application

### CLI Mode

Run the command-line version:

```bash
python main.py
```

### Streamlit UI

Run the web application:

```bash
streamlit run streamlit_app.py
```

Open the generated URL in your browser (typically `http://localhost:8501`).

---

## Quick Start

1. Start the application.
2. Upload one or more documents.
3. Build the knowledge base.
4. Ask questions about the uploaded content.
5. Receive grounded answers with citations.

Example queries:

```text
What is Self Attention?
```

```text
What is masked attention?
```

```text
Explain the architecture described in the document.
```

```text
Summarize the uploaded report.
```

---

## Project Structure

```text
multimodal_document_understanding/

├── ingestion/
├── layout/
├── extraction/
│   ├── table/
│   ├── figure/
│   └── ocr_correction/
├── cleaner/
├── document_post_processing/
├── section_building/
├── chunking/
├── embeddings/
├── retrieval/
├── reranking/
├── query_rewriting/
├── context_building/
├── generation/
├── mappings/
├── llm/
├── configurations/
├── data_models/
├── main.py
└── streamlit_app.py
...
