import faiss
import numpy as np
import os
from config.load_config import load_yaml_config

FAISS_INDEX_DIR = "faiss_indices" # Directory for storing client-specific indices
DIMENSION = 384  # Embedding dimension

# Store active client indices in memory
client_indices = {}

from sentence_transformers import SentenceTransformer
import numpy as np

# Load the model (can be reused across calls)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def generate_embedding(text):
    embedding = embedding_model.encode(text, convert_to_numpy=True)
    return embedding



def get_or_create_client_index(client_id):
    """Retrieve or create a FAISS index for a specific client."""
    if client_id not in client_indices:
        # Initialize FAISS index
        index = faiss.IndexFlatL2(DIMENSION)
        metadata = {}  # Metadata to map FAISS index IDs to responses
        
        # Load existing index and metadata if available
        index_path = os.path.join(FAISS_INDEX_DIR, f"{client_id}.index")
        metadata_path = os.path.join(FAISS_INDEX_DIR, f"{client_id}_metadata.npy")
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            index = faiss.read_index(index_path)
            metadata = np.load(metadata_path, allow_pickle=True).item()
        
        client_indices[client_id] = {"index": index, "metadata": metadata}
    
    return client_indices[client_id]

def add_embedding(client_id, embedding, response):
    """Add a new embedding and its response to the client's FAISS index."""
        # Check if the answer is negative
    if is_negative_response(response):
        print("Negative response detected. Not saving answer.")
        return None  # Do not save or return the answer
    client_data = get_or_create_client_index(client_id)
    index = client_data["index"]
    metadata = client_data["metadata"]

    # Convert embedding to NumPy array
    embedding = np.array([embedding], dtype="float32")

    # Add embedding to FAISS index
    index.add(embedding)

    # Store response in metadata
    metadata[len(metadata)] = response

    # Persist the updated index and metadata
    persist_client_index(client_id)

def search_embedding(client_id, query_embedding, k=5, similarity_threshold=0.5):
    """
    Search for similar embeddings in the client's FAISS index.
    Returns results sorted by similarity (higher threshold = lower distance).
    """
    client_data = get_or_create_client_index(client_id)
    index = client_data["index"]
    metadata = client_data["metadata"]

    # Convert query embedding to NumPy array
    query_embedding = np.array([query_embedding], dtype="float32")

    # Perform ANN search
    distances, indices = index.search(query_embedding, k)

    # Retrieve responses for indices within similarity threshold
    results = []
    for distance, idx in zip(distances[0], indices[0]):
        if idx != -1 and distance < similarity_threshold:  # Higher threshold -> Lower distance
            results.append((distance, metadata[idx]))  # Include distance for sorting

    # Sort results by distance (lower distance = closer match)
    results = sorted(results, key=lambda x: x[0])

    # Return only the responses (or include distances if needed)
    return [result[1] for result in results]


def update_embedding(client_id, embedding_idx, new_embedding, new_response):
    """Update an embedding and its response in the client's FAISS index."""
    client_data = get_or_create_client_index(client_id)
    index = client_data["index"]
    metadata = client_data["metadata"]

    # Remove old embedding (recreate the index without it)
    embeddings = index.reconstruct_n(0, index.ntotal)
    updated_embeddings = np.delete(embeddings, embedding_idx, axis=0)
    new_index = faiss.IndexFlatL2(DIMENSION)
    new_index.add(updated_embeddings)

    # Add new embedding
    new_embedding = np.array([new_embedding], dtype="float32")
    new_index.add(new_embedding)

    # Update metadata
    metadata[embedding_idx] = new_response

    # Replace the old index and metadata
    client_data["index"] = new_index
    persist_client_index(client_id)

def delete_embedding(client_id, embedding_idx):
    """Delete an embedding and its response from the client's FAISS index."""
    client_data = get_or_create_client_index(client_id)
    index = client_data["index"]
    metadata = client_data["metadata"]

    # Remove the embedding from the index
    embeddings = index.reconstruct_n(0, index.ntotal)
    updated_embeddings = np.delete(embeddings, embedding_idx, axis=0)
    new_index = faiss.IndexFlatL2(DIMENSION)
    new_index.add(updated_embeddings)

    # Remove metadata
    metadata.pop(embedding_idx)

    # Replace the old index and metadata
    client_data["index"] = new_index
    persist_client_index(client_id)

def persist_client_index(client_id):
    """Persist the FAISS index and metadata for a client."""
    client_data = client_indices[client_id]
    index = client_data["index"]
    metadata = client_data["metadata"]

    # Ensure the directory exists
    os.makedirs(FAISS_INDEX_DIR, exist_ok=True)

    # Save index to disk
    index_path = os.path.join(FAISS_INDEX_DIR, f"{client_id}.index")
    faiss.write_index(index, index_path)

    # Save metadata to disk
    metadata_path = os.path.join(FAISS_INDEX_DIR, f"{client_id}_metadata.npy")
    np.save(metadata_path, metadata)

def load_all_indices(config_path):
    """Load all client FAISS indices into memory on server startup."""
    global FAISS_INDEX_DIR
    config_dct = load_yaml_config(config_path)
    FAISS_INDEX_DIR = config_dct.get("model_cache_db_path", FAISS_INDEX_DIR)

    if not os.path.exists(FAISS_INDEX_DIR):
        os.makedirs(FAISS_INDEX_DIR)
    for filename in os.listdir(FAISS_INDEX_DIR):
        if filename.endswith(".index"):
            client_id = filename.replace(".index", "")
            get_or_create_client_index(client_id)



def is_negative_response(answer: str) -> bool:
    # Define negative response patterns to filter out
    negative_phrases = [
        "cannot be answered",
        "does not contain information",
        "appears nowhere",
        "cannot provide an answer"
    ]
    
    # Check if any negative phrase is present in the answer
    return any(phrase in answer.lower() for phrase in negative_phrases)
# Main execution for testing

# if __name__ == "__main__":
#     print("In Main")
    
#     # Load configuration and indices
#     config_path = "config/config.yaml"
#     load_all_indices(config_path)

#     # Define query and response
#     query = "what is rider policy?"
#     response = "A rider is a special policy for riding."

#     # Generate embedding for the query
#     embedding = generate_embedding(query)

#     # Search for similar embeddings
#     result = search_embedding("client1", embedding)
#     if not result:
#         print("Cache miss. Adding embedding.")
#         add_embedding("client1", embedding, response)
#     else:
#         print("found at once ", result)
#     # Define query and response
#     query = "what do you mean by rider policy?"
#     response = "A rider is a special policy for riding."

#     # Perform the search again to confirm addition
#     result = search_embedding("client2", embedding)
#     add_embedding("client2", embedding, response)
#     print("Search result:", result)