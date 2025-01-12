from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cachetools import TTLCache
from fastapi.middleware.cors import CORSMiddleware
from src_faq.embedding_db_builder.save_load_embeddings import load_embeddings_index,load_all_embeddings_indices
from src_faq.embedding_db_builder.create_embedding import EmbeddingService
from server.interactive_query_handler import InteractiveQueryHandler
from config.load_config import load_yaml_config
from src_model_cache.model_embedding_builder import load_all_indices,generate_embedding,add_embedding,search_embedding
import re
import os
import numpy as np

app = FastAPI()

# Allowable origins for CORS
origins = [
    "http://127.0.0.1:5000",  # Frontend running locally
    "http://localhost:5000",  # Alternative localhost frontend
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class QueryRequest(BaseModel):
    query: str
    client_id: str

# Global variables
interactive_engine = None
embedding_service_obj = None
db_index = None
db_indices = {}
abbreviation_mapping = {}
dist_thresh = None
cache = TTLCache(maxsize=1000, ttl=3600)
all_faq_answers = {}


# Helper function to preprocess user query
def preprocess_user_query(query, abbreviation_mapping):
    for abbr, full_form in abbreviation_mapping.items():
        query = re.sub(rf"\b{abbr}\b", full_form, query, flags=re.IGNORECASE)
    return query


# Helper function to map user query to embeddings
def map_user_query(query,client_id):
    global embedding_service_obj, db_index, dist_thresh, abbreviation_mapping

    if embedding_service_obj is None:
        raise ValueError("EmbeddingService object is not initialized.")
    # if db_index is None:
    #     raise ValueError("Database index is not loaded.")
    
    #client_id = "client1"
    if client_id in db_indices:
        db_index = db_indices[client_id]
        print(f"Embedding index for {client_id} loaded: {db_index}")
    else:
        print(f"No embedding index found for client: {client_id}")

    print(f"Preprocessing query: {query}")
    preprocessed_query = preprocess_user_query(query, abbreviation_mapping)
    print(f"Preprocessed query: {preprocessed_query}")

    # Generate embeddings for the preprocessed query
    query_embedding = embedding_service_obj.get_embeddings([preprocessed_query])
    norm_query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)
    #print(f"Normalized query embedding: {norm_query_embedding}")

    # Search for similar embeddings in the database
    distances, indices = db_index.search(norm_query_embedding.reshape(1, -1), k=1)
    print(f"Distances: {distances}, Indices: {indices}")

    index = int(indices[0][0])
    dist = float(distances[0][0])

    if dist < dist_thresh:
        return index, dist
    return None, dist


# Function to load answers from the text file
def load_answers(config_dct):
    answers = []
    answers_file_path = config_dct.get("lic_answers_path")

    if not answers_file_path or not os.path.exists(answers_file_path):
        print(f"Error: File not found or invalid path: {answers_file_path}")
        return answers

    try:
        with open(answers_file_path, "r", encoding="utf-8") as file:
            answers = [line.strip() for line in file.readlines() if line.strip()]
    except Exception as e:
        print(f"Error reading file {answers_file_path}: {e}")

    if not answers:
        print(f"No answers loaded from {answers_file_path}. Check file content.")

    return answers

import os

def load_all_answers(config_dct):

    answers_by_client = {}
    #base_dir = config_dct.get("documents_directory", "data_faq")
    base_dir = config_dct.get("lic_queries_path")
    if not base_dir or not os.path.exists(base_dir):
        print(f"Error: Base directory not found or invalid path: {base_dir}")
        return answers_by_client

    try:
        # Iterate over client folders in the base directory
        for client_folder in os.listdir(base_dir):
            client_folder_path = os.path.join(base_dir, client_folder)
            
            if not os.path.isdir(client_folder_path):
                continue  # Skip non-directory files

            # Construct the answers file path for the current client
            answers_file_path = os.path.join(client_folder_path, "answers.txt")
            
            if os.path.exists(answers_file_path):
                with open(answers_file_path, "r", encoding="utf-8") as file:
                    answers = [line.strip() for line in file.readlines() if line.strip()]
                    answers_by_client[client_folder] = answers
            else:
                print(f"Warning: No answers file found for client '{client_folder}' at {answers_file_path}")

    except Exception as e:
        print(f"Error while loading answers: {e}")

    if not answers_by_client:
        print(f"No answers loaded. Ensure that 'answers.txt' exists for each client folder in {base_dir}.")

    return answers_by_client



@app.on_event("startup")
def startup_event():
    global interactive_engine, embedding_service_obj, db_index, abbreviation_mapping, dist_thresh, all_faq_answers,db_indices

    try:
        print("Initializing server...")
        config_path_doc = "config/config.yaml"
        config_path_faq = "config/config_faq.yaml"
        config_dct_faq = load_yaml_config(config_path_faq)
        config_dct_main = load_yaml_config(config_path_doc) #main config to set models
        #load all indcies of model_cache
        load_all_indices(config_path_doc)

        use_llm_model = config_dct_main.get("use_LLM", False)  # Compilation flag to use LLM or not
        if use_llm_model:
            print(" *********** LLM model wil be used for all the clients ********* ")
            interactive_engine = InteractiveQueryHandler(config_path_doc)
            interactive_engine.init_global_rag_chain()
        else:
            print("*************** NO LLM Model Will BE USed for all the  Clients, Make Logic Separate for every Client **************")

        # Embedding service and database index
        embedding_service_obj = EmbeddingService(config_path_faq)
        #db_index = load_embeddings_index(config_dct)
        db_indices = load_all_embeddings_indices(config_dct_faq)
        #print(f"Embeddings index loaded: {db_index}")
        dist_thresh = config_dct_faq.get("dist_thresh", 0.5)  # Default value if missing
        # FAQ Answers
        all_faq_answers = load_all_answers(config_dct_faq)
        # if not faq_answers:
        #     raise RuntimeError("FAQ answers not loaded.")

        print("Server initialized successfully.")
    except Exception as e:
        print(f"Error during startup: {e}")
        raise RuntimeError("Server initialization failed.")


@app.post("/query")
async def query(request: QueryRequest):
    global interactive_engine, cache
    # Initialize the response object
    response = {"query": request.query, "response": None}

    try:
        # Validate the request input
        if not request.query:
            raise ValueError("Query is empty or not provided.")
        if not request.client_id:
            raise ValueError("Client ID is empty or not provided.")

        print(f"Received query: {request.query}")
        print(f"Client ID: {request.client_id}")

        # Cache mechanism right now local cache need to expiry policy if memory increase
        cache_key = f"{request.client_id}:{request.query}"  # Unique cache key based on client and query
        if cache_key in cache:
            print("Cache hit")
            response["response"] = cache[cache_key]
            return response

        # Check if the client ID exists in the FAQ answers dictionary
        if request.client_id not in all_faq_answers:
            raise ValueError(f"Client ID '{request.client_id}' not found in FAQ answers.")
        faq_answers = all_faq_answers[request.client_id]
        # Check if FAQ answers are loaded
        if len(faq_answers) == 0:
            raise ValueError(f"FAQ answers not loaded for client ID '{request.client_id}'.")

        # Map the query using embeddings
        index, dist = map_user_query(request.query,request.client_id)
        print(f"Index: {index}, Distance: {dist}")
        # Retrieve answer based on the mapped index
        if index is not None:
            if index < len(faq_answers):
                print("******** Answer found by FAQ Engine  ***********")
                answer = faq_answers[index]
            else:
                print(f"Index {index} out of range for FAQ answers list.")
                answer = "Answer not found."
        else:
            # Now query will go to model_cache to check the its cache if not found then update the cache
            # Generate embedding for the query
            embedding = generate_embedding(request.query)
            # Search for similar embeddings
            answer = search_embedding(request.client_id, embedding)
            if not answer:
                if interactive_engine is None:
                    print("***** interactive_engine Client not subscribed to use LLM Model*****")
                    answer = "Answere not found returning to Agent "
                    response["response"] = answer
                    return response
                print("*****Cache miss in Model Cache. Call to the Model FInally *****")
                answer = interactive_engine.handle_query(request.client_id, request.query)
                #add embedding to model cache
                add_embedding(request.client_id, embedding, answer)
            else:
                print("** Answer matched in Model Cache ****")
        # Cache the response
        cache[cache_key] = answer
        response["response"] = answer
        return response

    except KeyError as ke:
        error_message = f"Key error occurred: {ke}"
        print(error_message)
        raise HTTPException(status_code=404, detail=error_message)

    except ValueError as ve:
        error_message = f"Value error occurred: {ve}"
        print(error_message)
        raise HTTPException(status_code=400, detail=error_message)

    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
