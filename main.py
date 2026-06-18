import warnings

# Suppress PyTorch pin_memory warning on CPU-only systems
warnings.filterwarnings(
    "ignore",
    message=".*pin_memory.*"
)

# Suppress CPU fallback warnings
warnings.filterwarnings(
    "ignore",
    message=".*Neither CUDA nor MPS are available.*"
)

# Suppress HuggingFace unauthenticated request warning
warnings.filterwarnings(
    "ignore",
    message=".*unauthenticated requests to the HF Hub.*"
)

from download_models import download_prerequisites
from multimodal_RAG.multimodal_rag import MultimodalRAG

def print_menu():

    print("\n" + "=" * 50)
    print("Multimodal RAG")
    print("=" * 50)

    print("1. Process Single Document")
    print("2. Process Multiple Documents")
    print("3. Chat With RAG")
    print("4. View Documents")
    print("5. Delete Document")
    print("6. Reset Knowledge Base")
    print("7. Clear Conversation History")
    print("8. Update Configuration")
    print("\n9. Exit")


def chat_loop(rag):

    if not rag.mapper.has_documents():
        print("\nKnowledge base is empty.\nPlease upload documents first.\n")
        return

    print("\nType 'back' to return.\n")

    while True:

        query = input("You: ").strip()

        if not query:
            continue

        if query.lower() == "back":
            break

        response = rag.ask(query)

        print("\nAssistant:")
        print(response["answer"])

        if response.get("citations"):

            print("\nSources:")
            for source in response["citations"]:
                print(f"- {source['document_name']}")

        print()


def delete_document_menu(rag):

    documents = rag.mapper.get_documents_info()

    if not documents:
        print("\nNo documents found in the knowledge base.\n")
        return

    print("\nAvailable Documents:\n")

    for index, document in enumerate( documents, start=1):

        print(f"{index}. {document['document_name']}")
        print(f"   Pages    : {document['total_pages']}")
        print(f"   Chunks   : {document['total_chunks']}")
        print(f"   Sections : {document['total_sections']}")
        print(f"   Figures  : {document['total_figures']}")
        print(f"   Tables   : {document['total_tables']}")
        print()

    try:
        choice = int(input("\nSelect document number: "))

        document = documents[choice - 1]

        rag.delete_document(document["document_name"])

        print(f"\nDeleted: {document['document_name']}\n")

    except:
        print("\nInvalid selection.\n")


def process_single_document(rag):

    path = input("\nDocument Path: ").strip()

    print("\n", rag.process_document(path))


def process_multiple_documents(rag):

    print("\nEnter document paths (comma separated)\n")

    paths = input("Paths: ").strip()

    documents = [
        path.strip()
        for path in paths.split(",")
        if path.strip()
    ]

    print(
        rag.process_multiple_documents(
            documents
        )
    )


def show_documents(rag):

    documents = rag.mapper.get_documents_info()

    if not documents:
        print("\nNo documents found.\n")
        return

    print("\nKnowledge Base:\n")

    for document in documents:

        print(f"{document['document_name']}")
        print(f"   Pages    : {document['total_pages']}")
        print(f"   Chunks   : {document['total_chunks']}")
        print(f"   Sections : {document['total_sections']}")
        print(f"   Figures  : {document['total_figures']}")
        print(f"   Tables   : {document['total_tables']}")
        print()


def configuration_menu(rag):
    
    while True:
        config = rag.config

        print("\nCurrent Configuration\n")

        print(f"1. Retrieval Type     : {config['retrieval_type']}")
        print(f"2. Retrieval K        : {config['retrieval_k']}")
        print(f"3. Reranking K        : {config['reranking_k']}")
        print(f"4. Context Max Chunks : {config['context_max_chunks']}")
        print(f"5. Query Rewriting    : {config['enable_query_rewriting']}")
        print(f"6. Converstaion Max History    : {config['conversation_max_history']}")
        print(f"7. Assistant Response Mode     : {config['response_mode']}")
        print("\n8. Reset Configuration To Default")
        print(f"\n9. Back")

        choice = input("\nSelect Option: ").strip()

        if choice == "1":
            retrieval_type = input("\nEnter  (dense/sparse/hybrid): ").strip()

            if retrieval_type in ["dense", "sparse", "hybrid"]:
                config["retrieval_type"] = retrieval_type

        elif choice == "2":
            config["retrieval_k"] = int(input("\nRetrieval K: "))

        elif choice == "3":
            config["reranking_k"] = int(input("\nReranking K: "))

        elif choice == "4":
            config["context_max_chunks"] = int(input("\nContext Max Chunks: "))

        elif choice == "5":
            config["enable_query_rewriting"] = (not config["enable_query_rewriting"])
        
        elif choice == "6":
            config["conversation_max_history"] = int(input("\nConversation Max History: "))
            rag.update_memory_conf_and_history(config["conversation_max_history"])
        
        elif choice == "7":
            config["response_mode"] = input("\nEnter  (precise/detailed): ").strip()

        elif choice == "8":
            rag.config_manager.reset()
            print("\n Configurations set to Default. !!!")

        elif choice == "9":
            break

        rag.config_manager.save(config)
        rag.reload_config()


def main():

    GROQ_API_KEY = ""     # Ad your GROQ API KEY
    rag = MultimodalRAG(GROQ_API_KEY=GROQ_API_KEY)

    while True:

        print_menu()

        choice = input("\nSelect Option: ").strip()

        if choice == "1":
            process_single_document(rag)

        elif choice == "2":
            process_multiple_documents(rag)

        elif choice == "3":
            chat_loop(rag)

        elif choice == "4":
            show_documents(rag)

        elif choice == "5":
            delete_document_menu(rag)

        elif choice == "6":
            confirm = input("\nReset Knowledge Base? (y/n): ")

            if confirm.lower() == "y":
                rag.reset_knowledge_base()
                print("\nKnowledge Base Reset.\n")

        elif choice == "7":
            rag.clear_history()
            print("\nConversation History Cleared.\n")
        
        elif choice == "8":
            configuration_menu(rag)
            print("\nConfigurations Updated.")

        elif choice == "9":
            print("\nGoodbye.\n")
            break

        else:
            print("\nInvalid Option.\n")


if __name__ == "__main__":
    download_prerequisites()
    main()