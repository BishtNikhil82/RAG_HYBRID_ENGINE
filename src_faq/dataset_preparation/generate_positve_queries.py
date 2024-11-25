
import ollama

from transformers import AutoModelForCausalLM, AutoTokenizer

def generate_positive_queries_with_phi3(positive_queries, num_queries=100, model_name="microsoft/Phi-3-mini-4k-instruct", hf_token="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"):
    """
    Generates semantically similar queries for a given set of positive queries using Phi-3 model.

    Parameters:
    - positive_queries (list of str): List of base positive queries.
    - num_queries (int): Total number of queries to generate.
    - model_name (str): Name of the Hugging Face model.
    - hf_token (str): Hugging Face access token.

    Returns:
    - generated_queries (list of str): List of generated semantically similar queries.
    """
    # Load model and tokenizer with Hugging Face token
    tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=hf_token)
    model = AutoModelForCausalLM.from_pretrained(model_name, use_auth_token=hf_token)

    generated_queries = []
    for query in positive_queries[:min(len(positive_queries), num_queries)]:
        # Craft the prompt
        prompt = f"Paraphrase the following question to make it semantically similar:\n\nQuestion: {query}\n\nParaphrased:"
        
        # Tokenize input
        inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
        
        # Generate output
        outputs = model.generate(**inputs, max_length=512, num_return_sequences=1, temperature=0.5, top_p=0.9)
        paraphrased_query = tokenizer.decode(outputs[0], skip_special_tokens=True).split("Paraphrased:")[-1].strip()

        # Append to results
        generated_queries.append(paraphrased_query)

        # Stop if we reach the desired count
        if len(generated_queries) >= num_queries:
            break

    return generated_queries

# Load the positive queries from the LIC_Queries file
file_path = "data_faq/LIC_qeries.txt"  # Update this path to your file
with open(file_path, "r") as file:
    positive_queries = [line.strip() for line in file.readlines()]

# Generate 100 semantically similar queries
positive_semantic_queries = generate_positive_queries_with_phi3(positive_queries, num_queries=100)

# Save to a file for reference
output_positive_file = "positive_semantic_queries.txt"  # Update this to your desired file path
with open(output_positive_file, "w") as file:
    file.write("\n".join(positive_semantic_queries))

print(f"Semantically similar queries saved to {output_positive_file}")
