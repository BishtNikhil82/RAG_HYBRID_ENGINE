from langchain_community.vectorstores import Chroma
from src.vector_db_builder.document_splitter import split_documents
from src.loaders.main_load import Loader
#import fs_utils.file_system_utility as fsutils
from src.fs_utils import file_system_utility as fsutils
from  src.vector_db_builder.embeddings import get_embedding_model

# def create_chroma_db(docs_path_lst, config_dct):
#     obj_loader = Loader()
#     embedding_model = get_embedding_model(config_dct)

#     for idx, doc_path in enumerate(docs_path_lst):
#         doc_name, ext = fsutils.get_file_name_and_extension(doc_path)
#         documents = obj_loader.load(doc_path)
#         splits = split_documents(documents)

#         db_path = config_dct["vector_db_path"]
#         vectorstore = Chroma.from_documents(
#             documents=splits,
#             embedding=embedding_model,
#             persist_directory=db_path,
#             collection_name=doc_name  # Use document name as collection name
#         )
#         vectorstore.persist()
#         print(f"Document Id {idx+1} processed")


def create_chroma_db(docs_path_lst, config_dct, client_name):
    """
    Create a single collection in the vector database for all documents under a client.
    
    :param docs_path_lst: List of document paths for the client.
    :param config_dct: Configuration dictionary.
    :param client_name: Name of the client (used as the collection name).
    """
    obj_loader = Loader()
    embedding_model = get_embedding_model(config_dct)

    # List to accumulate all document splits for the client
    all_splits = []

    # Load and split each document
    for idx, doc_path in enumerate(docs_path_lst):
        doc_name, ext = fsutils.get_file_name_and_extension(doc_path)
        print(f"Processing document: {doc_name} (ID: {idx + 1})")
        
        # Load and split the document
        documents = obj_loader.load(doc_path)
        splits = split_documents(documents)
        
        # Accumulate splits
        all_splits.extend(splits)

    # Path to persist the vector database
    db_path = config_dct["vector_db_path"]
    
    # Create or load the Chroma vector store with the client name as the collection name
    vectorstore = Chroma.from_documents(
        documents=all_splits,
        embedding=embedding_model,
        persist_directory=db_path,
        collection_name=client_name  # Use client name as the collection name
    )
    
    # Persist the vector store
    vectorstore.persist()
    print(f"All documents for client '{client_name}' have been processed and stored in the vector database.")

def load_chroma_db(config_dct, collection_name_lst):
    embedding_model = get_embedding_model(config_dct)
    db_path = config_dct["vector_db_path"]
    # Dictionary to store in-memory collections
    collections_in_memory = {}
    for idx, collection_name in enumerate(collection_name_lst):
        collections_in_memory[collection_name] = Chroma(
            persist_directory=db_path,
            embedding_function=embedding_model,
            collection_name=collection_name
        )
    
    return collections_in_memory



