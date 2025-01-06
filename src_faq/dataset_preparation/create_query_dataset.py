import os
import pandas as pd
from config.load_config import load_yaml_config

def create_query_csv(config_dct):
    """
    Reads a file where each line corresponds to a query and writes a CSV file with QueryId and Query columns.
    """
    input_file = config_dct["lic_queries_path"]
    output_file = config_dct["lic_queries_dataset_path"]

    try:
        # Verify input file existence
        if not os.path.exists(input_file):
            print(f"Input file not found: {input_file}")
            return

        # Read the input file
        with open(input_file, 'r') as file:
            queries = file.readlines()

        # Debug: Print the queries read
        print("Queries read from input file:")
        #print(queries)

        if not queries:
            print("Input file is empty. No CSV will be created.")
            return

        # Create DataFrame
        data = {
            "QueryId": [f"Q{str(i+1).zfill(4)}" for i in range(len(queries))],
            "Query": [query.strip() for query in queries]
        }
        df = pd.DataFrame(data)

        # Debug: Print DataFrame
        #print("DataFrame content before writing to CSV:")
        #print(df)

        # Ensure output directory exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # Write to CSV
        df.to_csv(output_file, index=False)
        print(f"CSV file updated successfully: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    config_path = "config/config_faq.yaml"
    config_dct = load_yaml_config(config_path)
    create_query_csv(config_dct)
