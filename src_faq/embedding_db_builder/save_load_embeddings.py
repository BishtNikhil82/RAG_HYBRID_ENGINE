import faiss
import numpy as np

def write_embeddings(config_dct, embeddings):
    embeddings = np.array(embeddings).astype('float32')
    norm_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    # Create FAISS index
    index = faiss.IndexFlatL2(norm_embeddings.shape[1])  # L2 = Euclidean distance
    index.add(norm_embeddings)
    # Save FAISS index
    # positve_query_faiss_path = config_dct["positve_query_faiss_path"]
    # faiss.write_index(index, positve_query_faiss_path)
    faiss.write_index(index, config_dct["positve_query_faiss_path"])

# def load_embeddings_index(config_dct):
#     positve_query_faiss_path = config_dct["positve_query_faiss_path"]
#     embedding_index = faiss.read_index(positve_query_faiss_path)
#     return embedding_index
def load_embeddings_index(config_dct, client_id):
    """
    Load the FAISS index for a specific client.

    Args:
        config_dct (dict): Configuration dictionary.
        client_id (str): The ID of the client whose embeddings index is to be loaded.

    Returns:
        faiss.IndexFlatL2: Loaded FAISS index.
    """
    # Construct the path for the client's FAISS index
    faiss_dir = config_dct.get("faiss_db_directory", "faiss_db")  # Default directory for FAISS files
    positve_query_faiss_path = f"{faiss_dir}/{client_id}_positive_embeddings.faiss"

    # Load the FAISS index from the constructed path
    try:
        embedding_index = faiss.read_index(positve_query_faiss_path)
        print(f"Successfully loaded FAISS index for client: {client_id}")
        return embedding_index
    except Exception as e:
        raise ValueError(f"Failed to load FAISS index for client '{client_id}': {str(e)}")
    
def load_all_embeddings_indices(config_dct):
    """
    Load FAISS indices for all clients and return a dictionary mapping client IDs to their indices.

    Args:
        config_dct (dict): Configuration dictionary.

    Returns:
        dict: A dictionary where keys are client IDs and values are their corresponding FAISS indices.
    """
    faiss_dir = config_dct.get("faiss_db_directory", "faiss_db")  # Directory for FAISS files
    dist_thresh = config_dct.get("dist_thresh", 0.5)  # Default distance threshold
    client_indices = {}

    # List all FAISS files in the directory
    import os
    faiss_files = [
        f for f in os.listdir(faiss_dir) if f.endswith("_positive_embeddings.faiss")
    ]

    # Load each FAISS index and map it to the client ID
    for faiss_file in faiss_files:
        try:
            client_id = faiss_file.split("_positive_embeddings.faiss")[0]
            index_path = os.path.join(faiss_dir, faiss_file)
            client_indices[client_id] = faiss.read_index(index_path)
            print(f"Successfully loaded FAISS index for client: {client_id}")
        except Exception as e:
            print(f"Failed to load FAISS index for file {faiss_file}: {e}")

    return client_indices


