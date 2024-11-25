from src.loaders.main_load  import Loader
from src.fs_utils.file_system_utility import list_files
from src.vector_db_builder.chroma import create_chroma_db
from config.load_config import load_yaml_config

def process_documents(config_path):
    config_dct = load_yaml_config(config_path)
    documents_dir_path = config_dct["documents_directory"]
    docs_path_lst = list_files(documents_dir_path, ["pdf"])
    #doc_path = docs_path_lst[0]
    create_chroma_db(docs_path_lst, config_dct)

if __name__ == "__main__":
    print("In Main")
    config_path = "config/config.yaml"
    process_documents(config_path)