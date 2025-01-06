import re

# Function to clean and format the input file
def clean_and_format_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile:
        content = infile.read()
    
    # Extract all Query and Response pairs
    queries = re.findall(r"'Query:\s*(.*?)'", content, re.DOTALL)
    responses = re.findall(r"'Response:\s*(.*?)'", content, re.DOTALL)
    
    # Verify if the numbers of queries and responses match
    if len(queries) != len(responses):
        print("Mismatch between queries and responses. Please check the input file.")
        return
    
    # Open the output file to write formatted content
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for query, response in zip(queries, responses):
            formatted_entry = {
                "query": query.strip(),
                "response": response.strip()
            }
            outfile.write(f"{formatted_entry}\n")
    
    print(f"Formatted data has been saved to {output_file}")

# Input and output file paths
input_file = "data/policy_documents/input.txt"  # Replace with your input file path
output_file = "data/cleaned_data.txt"  # Replace with your output file path

# Run the cleaning and formatting function
clean_and_format_file(input_file, output_file)
