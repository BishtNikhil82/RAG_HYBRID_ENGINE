import numpy as np
from config.load_config import load_yaml_config
from src_faq.embedding_db_builder.save_load_embeddings import load_embeddings_index
from src_faq.embedding_db_builder.create_embedding import EmbeddingService

import re

def preprocess_user_query(query, abbreviation_mapping):
    """
    Preprocesses the user query to replace abbreviations with their full forms.

    Parameters:
    - query (str): The user query.
    - abbreviation_mapping (dict): Dictionary containing abbreviation-to-full-form mappings.

    Returns:
    - processed_query (str): Preprocessed user query.
    """
    #print(f"Original Query: {query}")
    for abbr, full_form in abbreviation_mapping.items():
        # Replace using regex for case-insensitivity
        query = re.sub(rf"\b{abbr}\b", full_form, query, flags=re.IGNORECASE)
    #print(f"Preprocessed Query: {query}")
    return query


def map_user_query(config_path):
    config_dct = load_yaml_config(config_path)
    db_index = load_embeddings_index(config_dct)
    embedding_service_obj = EmbeddingService(config_path)
    dist_thresh = config_dct["dist_thresh"]

    # Load abbreviation mapping
    abbreviation_mapping = config_dct.get("abbreviation_mapping", {})
    #print("Abbreviation Mapping Loaded:", abbreviation_mapping)

    while True:
        # Get the query from the user
        query = input("Enter your query (or type 'bye' to exit): ")
        if query.lower() == "bye":
            print("Goodbye!")
            break

        # Preprocess the query to handle abbreviations
        preprocessed_query = preprocess_user_query(query, abbreviation_mapping)
        print(preprocessed_query)
        # Generate embeddings for the preprocessed query
        query_embedding = embedding_service_obj.get_embeddings([preprocessed_query])
        norm_query_embedding = query_embedding / np.linalg.norm(query_embedding, axis=1, keepdims=True)

        # Search for similar embeddings in the database
        distances, indices = db_index.search(norm_query_embedding.reshape(1, -1), k=3)
        index = int(indices[0][0])
        dist = float(distances[0][0])

        if dist < dist_thresh:
            print(f"Map/Refer to Question No {index+1} with Distance = {dist}")
        else:
            print(f"Distance = {dist}")
            print("I’m sorry, that’s out of my area of expertise. Please reach out to our team.")

if __name__ == "__main__":
    config_path = "config/config_faq.yaml"
    map_user_query(config_path)
