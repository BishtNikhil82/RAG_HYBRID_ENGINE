from src.generator.create_prompt import get_prompt
from src.vector_db_builder.chroma import load_chroma_db
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama.llms import OllamaLLM
from src.fs_utils.file_system_utility import list_files, get_file_name_and_extension
from config.load_config import load_yaml_config

class InteractiveQueryHandler:
    def __init__(self, config_path):
        """
        Initialize the RAG Query Engine with preloaded collections.

        Args:
            config_path (str): Path to the configuration file.
        """
        # Load the configuration
        self.config_dct = load_yaml_config(config_path)

        # Preload all collections into memory
        self.collection_vectorstore_dct = self._load_all_collections()

        # Initialize the LLM
        self.llm = OllamaLLM(model=self.config_dct["llm_model"])

        # RAG chain for the current document
        self.rag_chain = None

    def get_collection_name_lst(self):
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

        Returns:
            dict: A dictionary mapping collection names to their vector stores.
        """
        collection_name_lst = self.get_collection_name_lst()
        collection_vectorstore_dct = load_chroma_db(self.config_dct, collection_name_lst)
        return collection_vectorstore_dct

    def init_interactive_loop(self, doc_name):
        """
        Initialize the interactive loop for a specific document.

        Args:
            doc_name (str): Name of the document/collection to set up the RAG chain.
        """
        # Ensure the collection exists in memory
        if doc_name not in self.collection_vectorstore_dct:
            raise ValueError(f"Document '{doc_name}' not found in collections.")

        # Fetch the vector store for the document and set up the RAG chain
        vectorstore = self.collection_vectorstore_dct[doc_name]
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        prompt = get_prompt()
        self.rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

        print(f"Interactive loop initialized for document: {doc_name}")

        # Start the interactive query-answering loop
        self._interactive_query_loop()

    def _interactive_query_loop(self):
        """
        Start the interactive query-answering loop for the current RAG chain.
        """
        if not self.rag_chain:
            raise ValueError("RAG chain is not initialized. Call `init_interactive_loop` first.")

        while True:
            query = input("Enter your query (or type 'bye' to exit): ")
            if query.lower() == "bye":
                print("Goodbye!")
                break

            # Use the initialized RAG chain to answer the query
            response = self.rag_chain.invoke(query)
            print("Response:", response)
            print("Next")

if __name__ == "__main__":
    config_path = "config/config.yaml"
    # Instantiate the RAGQueryEngine
    engine = InteractiveQueryHandler(config_path)

    # Initialize the interactive loop with a specific document name
    doc_name = "512N277V02" #input("Enter the document name to load: ")
    try:
        engine.init_interactive_loop(doc_name)
    except ValueError as e:
        print(e)
