import pandas as pd
from config.load_config import load_yaml_config
from src_faq.dataset_preparation.create_query_dataset import create_query_csv
from src_faq.embedding_db_builder.save_load_embeddings import write_embeddings
from src_faq.embedding_db_builder.create_embedding import EmbeddingService
import os
# def generate_and_save_embeddings_faiss(config_path):
#     config_dct = load_yaml_config(config_path)
#     is_create_dataset = config_dct["is_create_dataset"]
#     #print("creating dataset check")
#     #if is_create_dataset:
#     print("creating dataset")
#     create_query_csv(config_dct)

#     lic_queries_csv_path = config_dct["lic_queries_dataset_path"]
#     df = pd.read_csv(lic_queries_csv_path)
#     query_lst = df["Query"].to_list()
#     #query_lst = query_lst[0:20]
#     embed_obj = EmbeddingService(config_path)
#     query_embeddings = embed_obj.get_embeddings(query_lst)
#     write_embeddings(config_dct, query_embeddings)


# if __name__ == "__main__":
#     config_path = "config/config_faq.yaml"
#     generate_and_save_embeddings_faiss(config_path)



def generate_and_save_embeddings_faiss(config_path):
    """
    Generate and save FAISS embeddings for all client folders in the data_faq directory.

    Args:
        config_path (str): Path to the configuration file.
    """
    config_dct = load_yaml_config(config_path)
    data_faq_dir = config_dct["lic_queries_path"].rsplit("/", 1)[0]  # Get base folder path (e.g., data_faq)

    # Iterate over each client folder in the base directory
    for client_folder in os.listdir(data_faq_dir):
        client_path = os.path.join(data_faq_dir, client_folder)
        
        if not os.path.isdir(client_path):  # Skip if not a directory
            continue

        print(f"Processing client: {client_folder}")

        # Update paths in the configuration for the current client
        config_dct["lic_queries_path"] = os.path.join(client_path, "LIC_qeries.txt")
        config_dct["lic_answers_path"] = os.path.join(client_path, "answers.txt")
        config_dct["lic_queries_dataset_path"] = os.path.join(client_path, "lic_queries_dataset.csv")
        config_dct["positve_query_faiss_path"] = os.path.join("faiss_db", f"{client_folder}_positive_embeddings.faiss")
        config_dct["neg_query_faiss_path"] = os.path.join("faiss_db", f"{client_folder}_negative_embeddings.faiss")

        # Create query dataset for the client
        print(f"Creating query dataset for client: {client_folder}")
        create_query_csv(config_dct)

        # Generate embeddings
        lic_queries_csv_path = config_dct["lic_queries_dataset_path"]
        if not os.path.exists(lic_queries_csv_path):
            print(f"No dataset found for client: {client_folder}. Skipping...")
            continue

        df = pd.read_csv(lic_queries_csv_path)
        query_lst = df["Query"].to_list()
        embed_obj = EmbeddingService(config_path)
        query_embeddings = embed_obj.get_embeddings(query_lst)

        # Save embeddings to FAISS
        print(f"Saving FAISS embeddings for client: {client_folder}")
        write_embeddings(config_dct, query_embeddings)


if __name__ == "__main__":
    config_path = "config/config_faq.yaml"
    generate_and_save_embeddings_faiss(config_path)
