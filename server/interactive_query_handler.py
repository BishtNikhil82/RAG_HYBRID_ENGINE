from langchain.embeddings import SentenceTransformerEmbeddings
from src.vector_db_builder.chroma import load_chroma_db
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama.llms import OllamaLLM
from src.fs_utils.file_system_utility import list_files, get_file_name_and_extension
from config.load_config import load_yaml_config
from src.generator.create_prompt import get_prompt
from openai import OpenAI
from openai import api_key as openai_api_key
import os
from langchain.chat_models import ChatOpenAI


def merge_retrievers(retrievers):
    def combined_retriever(query):
        results = []
        for retriever in retrievers:
            results.extend(retriever.invoke(query))
        return results
    return combined_retriever


class InteractiveQueryHandler:
    def __init__(self, config_path):
        self.config_dct = load_yaml_config(config_path)
        #self.embedding_function = self._initialize_embedding_function()
        self.collection_vectorstore_dct = self._load_all_collections()
        #self.llm = OllamaLLM(model=self.config_dct["llm_model"],temperature=0.3,max_output_length=100 )
        self.llm = None
        self.rag_chain = None

    # def _initialize_embedding_function(self):
    #     embedding_model_name = self.config_dct.get("embedding_model", "all-MiniLM-L6-v2")
    #     return SentenceTransformerEmbeddings(model_name=embedding_model_name)


    def _load_all_collections(self):
        """
        Load all collections into a dictionary.

        Returns:
            dict: A dictionary mapping collection names to their vector stores.
        """
        collection_name_lst = self.get_collection_name_lst()
        collection_vectorstore_dct = load_chroma_db(self.config_dct, collection_name_lst)
        return collection_vectorstore_dct
    
    def set_llm_model(self):
        use_openai = self.config_dct.get("use_openai", False)  # Compilation flag, default is False
        if use_openai:
            print("*************** Using OpenAI for LLM **********")
            os.environ["OPENAI_API_KEY"] = self.config_dct.get("OPENAI_API_KEY")
            self.llm = ChatOpenAI(temperature=0.7, model_name=self.config_dct.get("gpt_model"))
            # openai_api_key = self.config_dct.get("OPENAI_API_KEY")
            # self.llm = OpenAI(
            #     model_name=self.config_dct.get("gpt_model"),  # Example: "gpt-3.5-turbo" or "gpt-4"
            #     temperature=0.7,  # Adjust as per requirement
            #     openai_api_key=openai_api_key,
            # )
        else:
            print("******************** Using Ollama for LLM ************************")
            self.llm = OllamaLLM(model=self.config_dct["llm_model"])

    
    def init_global_rag_chain(self):
        self.set_llm_model()
        prompt = get_prompt()
        self.rag_chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )



    def invoke_query(self, query):
        if not self.rag_chain:
            raise ValueError("RAG chain is not initialized. Call `init_global_rag_chain` first.")
        print(f"Invoking RAG chain for query: {query}")
        result = self.rag_chain.invoke(query)
        print(f"RAG chain result: {result}")
        return result


    def handle_query(self, client_id, query):
        """
        Handle a query dynamically by selecting the appropriate collection.

        Args:
            collection_name (str): Name of the collection (e.g., client1, client2).
            query (str): The user's query.

        Returns:
            str: The RAG chain's response.
        """
        # Ensure the collection exists
        if client_id not in self.collection_vectorstore_dct:
            raise ValueError(f"Collection '{client_id}' not found.")

        # Update retriever for the selected collection
        vectorstore = self.collection_vectorstore_dct[client_id]
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

        # Update the RAG chain with the dynamic retriever
        response = self.rag_chain.invoke({"context": retriever.invoke(query), "question": query})

        return response
    
    def get_collection_name_lst(self):
        """
        Retrieve the list of collection names, which correspond to client folder names.

        :return: List of collection names (client folder names).
        """
        documents_dir_path = self.config_dct["documents_directory"]
        
        # Check if the documents directory exists and is a directory
        if os.path.exists(documents_dir_path) and os.path.isdir(documents_dir_path):
            # Get all subdirectory names (client folders)
            collection_name_lst = [
                folder_name
                for folder_name in os.listdir(documents_dir_path)
                if os.path.isdir(os.path.join(documents_dir_path, folder_name))
            ]
            return collection_name_lst
        else:
            print(f"Error: '{documents_dir_path}' does not exist or is not a directory.")
            return []
