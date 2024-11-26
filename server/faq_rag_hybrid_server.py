from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cachetools import TTLCache
from config.load_config import load_yaml_config
from src_faq.embedding_db_builder.save_load_embeddings import load_embeddings_index
from src_faq.embedding_db_builder.create_embedding import EmbeddingService
from server.interactive_query_handler import InteractiveQueryHandler
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import re
import os

app = FastAPI()
# Allowable origins for CORS
origins = [
    "http://127.0.0.1:5000",  # Frontend running locally
    "http://localhost:5000", # Alternative localhost frontend
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str

# Global variables
interactive_engine = None
embedding_service_obj = None
db_index = None
abbreviation_mapping = {}
dist_thresh = None
cache = TTLCache(maxsize=1000, ttl=3600)
faq_answers = []  # List to store answers loaded from the text file

# Helper function: Preprocess user query
def preprocess_user_query(query, abbreviation_mapping):
    for abbr, full_form in abbreviation_mapping.items():
        query = re.sub(rf"\b{abbr}\b", full_form, query, flags=re.IGNORECASE)
    return query

# Helper function: Map user query using embeddings
def map_user_query(query):
    """
    Maps the user query to the closest question in the embeddings database.
    Returns the mapped question index if distance is below the threshold, otherwise None.
    """
    global embedding_service_obj, db_index, dist_thresh, abbreviation_mapping

    # Preprocess the query to handle abbreviations
    preprocessed_query = preprocess_user_query(query, abbreviation_mapping)

    # Generate embeddings for the preprocessed query
    query_embedding = embedding_service_obj.get_embeddings([preprocessed_query])
    norm_query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)

    # Search for similar embeddings in the database
    distances, indices = db_index.search(norm_query_embedding.reshape(1, -1), k=1)
    index = int(indices[0][0])
    dist = float(distances[0][0])

    if dist < dist_thresh:
        return index, dist  # Mapped index and distance
    return None, dist  # No mapping found

# Function to load answers from the text file
def load_answers(config_dct):
    """
    Function to load answers from a file based on a path provided in the config dictionary.

    :param config_dct: Dictionary containing the configuration with the key 'lic_answers_path'.
    :return: List of answers loaded from the file.
    """
    answers = []  # Initialize an empty list for answers

    # Retrieve the file path from the config dictionary
    answers_file_path = config_dct.get("lic_answers_path")
    print(f"Answers file path from config: {answers_file_path}")

    # Check if the path is valid
    if not answers_file_path or not os.path.exists(answers_file_path):
        print(f"Error: File not found or invalid path: {answers_file_path}")
        return answers  # Return an empty list

    # Try reading the file
    try:
        with open(answers_file_path, "r", encoding="utf-8") as file:
            answers = [line.strip() for line in file.readlines() if line.strip()]  # Avoid blank lines
        print(f"Loaded {len(answers)} answers from {answers_file_path}")
    except FileNotFoundError:
        print(f"Error: File not found at {answers_file_path}")
    except UnicodeDecodeError:
        print(f"Error: File encoding issue for {answers_file_path}. Trying a different encoding...")
        try:
            with open(answers_file_path, "r", encoding="latin-1") as file:
                answers = [line.strip() for line in file.readlines() if line.strip()]
            print(f"Loaded {len(answers)} answers from {answers_file_path} using fallback encoding.")
        except Exception as e:
            print(f"Failed to read file {answers_file_path} with fallback encoding: {e}")
    except Exception as e:
        print(f"Error reading file {answers_file_path}: {e}")

    # Validate loaded answers
    if not answers:
        print(f"Error: No answers loaded from {answers_file_path}. Check file content.")

    # Optionally print the first few answers for validation
    else:
        print(f"First 5 answers: {answers[:5]}")

    return answers

@app.on_event("startup")
def startup_event():
    """
    Initialize all global variables and resources on server startup.
    """
    global interactive_engine, embedding_service_obj, db_index, abbreviation_mapping, dist_thresh, faq_answers

    try:
        # Load configuration
        config_path_doc = "config/config.yaml"
        config_path_faq = "config/config_faq.yaml"
        config_dct = load_yaml_config(config_path_faq)

        # Initialize interactive query handler
        interactive_engine = InteractiveQueryHandler(config_path_doc)
        interactive_engine.init_global_rag_chain()

        # Initialize embedding service and database index
        embedding_service_obj = EmbeddingService(config_path_faq)
        db_index = load_embeddings_index(config_dct)

        # Load abbreviation mapping and distance threshold
        abbreviation_mapping = config_dct.get("abbreviation_mapping", {})
        dist_thresh = config_dct["dist_thresh"]

        # Load answers from the text file
        faq_answers = load_answers(config_dct)

        if not faq_answers:
            raise RuntimeError("Failed to load FAQ answers. Please check the answers file.")

        print("Server initialized successfully.")
    except Exception as e:
        print(f"Error during startup: {str(e)}")
        raise RuntimeError("Server failed to start due to initialization error.")

@app.post("/query")
async def query(request: QueryRequest):
    """
    Handle a query by first attempting to map it to an existing FAQ index.
    If no mapping is found, fallback to InteractiveQueryHandler.
    """
    global interactive_engine, cache, faq_answers

    cache_key = request.query
    try:
        # Check cache
        if cache_key in cache:
            print("************ Query TO CACHE *******************")
            return {"query": request.query, "response": cache[cache_key]}

        # Step 1: Try to map the query using embeddings
        index, dist = map_user_query(request.query)
        print(f"********* INDEX = {index} ***********")

        if len(faq_answers) == 0:
            print("Error: FAQ answers list is empty during query processing.")
            raise HTTPException(status_code=500, detail="FAQ answers not loaded. Please check the initialization.")
        if index is not None:
            print(f"Total answers loaded: {len(faq_answers)}")
            print("************ Query TO FAQ engine *******************")
            if index < len(faq_answers):
                answer = faq_answers[index]
            else:
                print(f"Index {index} is out of range for answers list of length {len(faq_answers)}.")
                answer = "Answer not found."
            #response = {"query": request.query, "mapped_question_index": index, "distance": dist, "answer": answer}
            response = answer
        else:
            # Step 2: Fallback to InteractiveQueryHandler if no mapping found
            print("************** Query TO  DOC engine *******************")
            response = interactive_engine.invoke_query(request.query)

        # Cache the response
        cache[cache_key] = response
        print(response)
        return {"query": request.query, "response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
