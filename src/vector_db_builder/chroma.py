
from langchain.vectorstores import Chroma
from src.vector_db_builder.document_splitter import split_documents
from src.loaders.main_load import Loader
#import fs_utils.file_system_utility as fsutils
from src.fs_utils import file_system_utility as fsutils
from  src.vector_db_builder.embeddings import get_embedding_model

def create_chroma_db(docs_path_lst, config_dct):
    obj_loader = Loader()
    embedding_model = get_embedding_model(config_dct)

    for idx, doc_path in enumerate(docs_path_lst):
        doc_name, ext = fsutils.get_file_name_and_extension(doc_path)
        documents = obj_loader.load(doc_path)
        splits = split_documents(documents)

        db_path = config_dct["vector_db_path"]
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embedding_model,
            persist_directory=db_path,
            collection_name=doc_name  # Use document name as collection name
        )
        vectorstore.persist()
        print(f"Document Id {idx+1} processed")

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




