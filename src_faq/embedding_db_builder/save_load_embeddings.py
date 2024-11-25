import faiss
import numpy as np

def write_embeddings(config_dct, embeddings):
    embeddings = np.array(embeddings).astype('float32')
    norm_embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    # Create FAISS index
    index = faiss.IndexFlatL2(norm_embeddings.shape[1])  # L2 = Euclidean distance
    index.add(norm_embeddings)
    # Save FAISS index
    positve_query_faiss_path = config_dct["positve_query_faiss_path"]
    faiss.write_index(index, positve_query_faiss_path)

def load_embeddings_index(config_dct):
    positve_query_faiss_path = config_dct["positve_query_faiss_path"]
    embedding_index = faiss.read_index(positve_query_faiss_path)
    return embedding_index

