import pandas as pd
from config.load_config import load_yaml_config

def create_query_csv(config_dct):
    """
    Reads a file where each line corresponds to a query and writes a CSV file with QueryId and Query columns.
    """
    input_file = config_dct["lic_queries_path"]
    output_file = config_dct["lic_queries_dataset_path"]
    
    try:
        # Read the file
        with open(input_file, 'r') as file:
            queries = file.readlines()
        
        # Create DataFrame with QueryId and Query
        data = {
            "QueryId": [f"Q{str(i+1).zfill(4)}" for i in range(len(queries))],  # String ID Q0001, Q0002, ...
            "Query": [query.strip() for query in queries]
        }
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv(output_file, index=False)
        print(f"CSV file created successfully: {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    config_path = "config/config_faq.yaml"
    config_dct = load_yaml_config(config_path)
    create_query_csv(config_dct)
