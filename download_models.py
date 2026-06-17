import os

import gdown
from sentence_transformers import SentenceTransformer
from sentence_transformers.cross_encoder import CrossEncoder


def create_directories():
    os.makedirs("models/embeddings", exist_ok=True)
    os.makedirs("models/rerankers", exist_ok=True)
    os.makedirs("models/layout", exist_ok=True)


def create_storage_directories():
    for dir in ["data", "data/raw_documents", "data/chunk_data", "data/converted_documents", "data/documents_images", 
                "data/embedding_storage", "data/embedding_storage/chroma", "data/embedding_storage/bm25",
                "data/figure_debugging", "data/table_debugging", "data/mappings"]:

        os.makedirs(dir, exist_ok=True)


def model_exists(model_path):
    return os.path.exists(
        os.path.join(model_path, "config.json")
    )


def download_embedding_model():

    model_name = "BAAI/bge-base-en-v1.5"
    save_path = "models/embeddings/bge-base-en-v1.5"

    if model_exists(save_path):
        print(f"Embedding model already exists: {save_path}")
        return

    print(f"Downloading {model_name}...")

    model = SentenceTransformer(model_name)
    model.save(save_path)

    print(f"Saved embedding model to {save_path}")


def download_reranker_models():

    rerankers = [
        (
            "cross-encoder/ms-marco-MiniLM-L-6-v2",
            "models/rerankers/ms-marco-MiniLM-L-6-v2"
        ),
        (
            "BAAI/bge-reranker-base",
            "models/rerankers/bge-reranker-base"
        )
    ]

    for model_name, save_path in rerankers:

        if model_exists(save_path):
            print(f"Reranker already exists: {save_path}")
            continue

        print(f"Downloading {model_name}...")

        model = CrossEncoder(model_name)
        model.save(save_path)

        print(f"Saved to {save_path}")


def download_layout_model():

    save_path = "models/layout/doclayout_yolo_ft.pt"

    if os.path.exists(save_path):
        print(f"Layout model already exists: {save_path}")
        return

    # Replace with your Google Drive file ID
    file_id = "1jWADlbEukps--JX4Qves-qWW-cuc4OPz"

    print("Downloading DocLayout-YOLO model...")

    gdown.download(
        f"https://drive.google.com/uc?id={file_id}",
        save_path,
        quiet=False
    )

    print(f"Saved layout model to {save_path}")


def download_prerequisites():

    create_directories()
    create_storage_directories()

    download_embedding_model()
    download_reranker_models()
    download_layout_model()

    print("\nSetup completed successfully.")


if __name__ == "__main__":
    download_prerequisites()