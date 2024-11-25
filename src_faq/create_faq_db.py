import pandas as pd
from config.load_config import load_yaml_config
from src_faq.dataset_preparation.create_query_dataset import create_query_csv
from src_faq.embedding_db_builder.save_load_embeddings import write_embeddings
from src_faq.embedding_db_builder.create_embedding import EmbeddingService

def generate_and_save_embeddings_faiss(config_path):
    config_dct = load_yaml_config(config_path)
    is_create_dataset = config_dct["is_create_dataset"]
    if is_create_dataset:
        create_query_csv(config_dct)

    lic_queries_csv_path = config_dct["lic_queries_dataset_path"]
    df = pd.read_csv(lic_queries_csv_path)
    query_lst = df["Query"].to_list()
    #query_lst = query_lst[0:20]
    embed_obj = EmbeddingService(config_path)
    query_embeddings = embed_obj.get_embeddings(query_lst)
    write_embeddings(config_dct, query_embeddings)


if __name__ == "__main__":
    config_path = "config/config_faq.yaml"
    generate_and_save_embeddings_faiss(config_path)
