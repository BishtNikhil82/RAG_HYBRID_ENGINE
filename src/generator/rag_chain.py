from src.generator.create_prompt import get_prompt
from src.vector_db_builder.chroma import load_chroma_db
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama.llms import OllamaLLM
from src.fs_utils.file_system_utility import list_files, get_file_name_and_extension

def get_collection_name(config_dct):
    documents_dir_path = config_dct["documents_directory"]
    docs_path_lst = list_files(documents_dir_path, ["pdf"])
    collection_name_lst = []
    for doc_path in docs_path_lst:
        doc_name, ext = get_file_name_and_extension(doc_path)
        collection_name_lst.append(doc_name)
    
    return collection_name_lst

def get_document_vecotre_store(config_dct, doc_name):
    collection_name_lst = get_collection_name(config_dct)
    collection_vectorstore_dct = load_chroma_db(config_dct, collection_name_lst)
    collection_name = doc_name
    vectorstore = collection_vectorstore_dct[collection_name]
    return vectorstore

def get_rag_chain(config_dct, doc_name):
    prompt = get_prompt()
    vectorstore = get_document_vecotre_store(config_dct, doc_name)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    #docs = retriever.invoke("What is Appointee ?")
    #print(len(docs))
    llm_model_name = config_dct["llm_model"]
    llm = OllamaLLM(model=llm_model_name)
    rag_chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain