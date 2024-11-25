from langchain.chains import RetrievalQA
from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama.llms import OllamaLLM
from src.fs_utils.file_system_utility import list_files, get_file_name_and_extension
from config.load_config import load_yaml_config
from src.generator.create_prompt import get_prompt


def merge_retrievers(retrievers):
    """
    Merge multiple retrievers into a single callable retriever.
    """
    def combined_retriever(query):
        results = []
        for retriever in retrievers:
            results.extend(retriever.get_relevant_documents(query))
        return results

    return combined_retriever


class InteractiveQueryHandler:
    def __init__(self, config_path):
        """
        Initialize the RAG Query Engine with preloaded collections.
        """
        self.config_dct = load_yaml_config(config_path)
        self.embedding_function = self._initialize_embedding_function()
        self.collection_vectorstore_dct = self._load_all_collections()
        self.llm = OllamaLLM(model=self.config_dct["llm_model"])
        self.rag_chain = None

    def _initialize_embedding_function(self):
        """
        Initialize the embedding function using SentenceTransformer.
        """
        embedding_model_name = self.config_dct.get("embedding_model", "all-MiniLM-L6-v2")
        return SentenceTransformerEmbeddings(model_name=embedding_model_name)

    def get_collection_name_lst(self):
        """
        Retrieve a list of collection names (document names) from the documents directory.
        """
        documents_dir_path = self.config_dct["documents_directory"]
        docs_path_lst = list_files(documents_dir_path, ["pdf"])
        collection_name_lst = []
        for doc_path in docs_path_lst:
            doc_name, ext = get_file_name_and_extension(doc_path)
            collection_name_lst.append(doc_name)
        return collection_name_lst

    def _load_all_collections(self):
        """
        Load all collections into a dictionary.
        """
        collection_name_lst = self.get_collection_name_lst()
        print(f"Found collections: {collection_name_lst}")
        collection_vectorstore_dct = {
            collection_name: Chroma(
                collection_name=collection_name,
                embedding_function=self.embedding_function,
                persist_directory=self.config_dct.get("vector_db_path", "db")
            )
            for collection_name in collection_name_lst
        }
        print("Collections loaded successfully.")
        return collection_vectorstore_dct

    def init_global_rag_chain(self):
        """
        Initialize the RAG chain for querying across all loaded documents.
        """
        all_retrievers = [
            vectorstore.as_retriever(search_kwargs={"k": 3})
            for vectorstore in self.collection_vectorstore_dct.values()
        ]
        merged_retriever = merge_retrievers(all_retrievers)

        prompt = get_prompt()
        self.rag_chain = (
            {"context": merged_retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        print("Global RAG chain initialized successfully.")

    def invoke_query(self, query):
        """
        Use the global RAG chain to handle a query.
        """
        if not self.rag_chain:
            raise ValueError("RAG chain is not initialized. Call `init_global_rag_chain` first.")
        return self.rag_chain.invoke(query)
