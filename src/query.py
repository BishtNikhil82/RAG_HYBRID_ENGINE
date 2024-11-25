from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.generator.create_prompt import get_prompt
from src.vector_db_builder.chroma import load_chroma_db
from src.fs_utils.file_system_utility import list_files, get_file_name_and_extension
from config.load_config import load_yaml_config
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama.llms import OllamaLLM
from cachetools import TTLCache

# Initialize FastAPI app
app = FastAPI()

# Define the Request Model for querying
class QueryRequest(BaseModel):
    query: str
    doc_name: str

# Global Variables
interactive_engine = None
cache = TTLCache(maxsize=1000, ttl=3600)  # Cache with a 1-hour TTL


class InteractiveQueryHandler:
    def __init__(self, config_path):
        """
        Initialize the RAG Query Engine with preloaded collections.
        """
        self.config_dct = load_yaml_config(config_path)
        self.collection_vectorstore_dct = self._load_all_collections()
        self.llm = OllamaLLM(model=self.config_dct["llm_model"])
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
        collection_name_lst = self.get_collection_name_lst()
        collection_vectorstore_dct = load_chroma_db(self.config_dct, collection_name_lst)
        return collection_vectorstore_dct

    def init_rag_chain(self, doc_name):
        """
        Initialize the RAG chain for a specific document.
        """
        if doc_name not in self.collection_vectorstore_dct:
            raise ValueError(f"Document '{doc_name}' not found in collections.")

        vectorstore = self.collection_vectorstore_dct[doc_name]
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        prompt = get_prompt()
        self.rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )

    def invoke_query(self, query):
        """
        Use the RAG chain to handle a query.
        """
        if not self.rag_chain:
            raise ValueError("RAG chain is not initialized. Call `init_rag_chain` first.")
        return self.rag_chain.invoke(query)


@app.on_event("startup")
def startup_event():
    """
    Load configuration and initialize the InteractiveQueryHandler.
    """
    global interactive_engine
    config_path = "config/config.yaml"
    try:
        print("Loading configuration...")
        interactive_engine = InteractiveQueryHandler(config_path)
        print("InteractiveQueryHandler initialized successfully.")
    except Exception as e:
        print(f"Failed to initialize InteractiveQueryHandler: {e}")
        raise RuntimeError("Server failed to start due to initialization error.")


@app.post("/query")
async def query(request: QueryRequest):
    """
    Handle a query for a specific document.
    """
    global interactive_engine, cache

    # Cache key combines the document name and query
    cache_key = (request.query, request.doc_name)

    try:
        # Return cached response if available
        if cache_key in cache:
            return {"query": request.query, "response": cache[cache_key]}

        # Initialize RAG chain for the requested document if not already initialized
        interactive_engine.init_rag_chain(request.doc_name)

        # Invoke the query using the RAG chain
        response = interactive_engine.invoke_query(request.query)

        # Cache the result and return it
        cache[cache_key] = response
        return {"query": request.query, "response": response}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=5000)
