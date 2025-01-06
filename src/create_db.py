from src.loaders.main_load  import Loader
from src.fs_utils.file_system_utility import list_files
from src.vector_db_builder.chroma import create_chroma_db
from config.load_config import load_yaml_config

import os

def process_documents(config_path):
    # Load the configuration
    config_dct = load_yaml_config(config_path)
    
    # Base directory containing client folders
    documents_dir_path = config_dct["documents_directory"]
    print(f"Base Documents Directory Path: {documents_dir_path}")
    
    # Iterate over each client folder in the base directory
    if os.path.exists(documents_dir_path) and os.path.isdir(documents_dir_path):
        client_folders = [f for f in os.listdir(documents_dir_path) 
                          if os.path.isdir(os.path.join(documents_dir_path, f))]
        
        for client_folder in client_folders:
            client_folder_path = os.path.join(documents_dir_path, client_folder)
            print(f"\nProcessing documents for client: {client_folder}")
            
            # Get the list of document paths in the client folder
            docs_path_lst = list_files(client_folder_path, ["pdf"])
            
            # Print all the documents in the client folder
            if docs_path_lst:
                print(f"Documents for {client_folder}:")
                for doc in docs_path_lst:
                    print(f"- {doc}")
            else:
                print(f"No documents found for {client_folder}.")
            
            # Call create_chroma_db for the client's documents
            create_chroma_db(docs_path_lst, config_dct,client_folder)
    else:
        print(f"Error: Base directory '{documents_dir_path}' does not exist or is not a directory.")


if __name__ == "__main__":
    print("In Main")
    config_path = "config/config.yaml"
    process_documents(config_path)