import random

def generate_negative_queries(positive_queries, num_queries=100):
    """
    Generates a set of negative queries by modifying the provided positive queries.

    Parameters:
    - positive_queries (list of str): List of positive queries.
    - num_queries (int): Number of negative queries to generate.

    Returns:
    - negative_queries (list of str): List of generated negative queries.
    """
    irrelevant_contexts = [
        "school fees",
        "car loans",
        "investment advice",
        "home loans",
        "mutual funds",
        "internet issues",
        "bank-related queries",
        "complaints about agents",
        "stock trading",
        "real estate investments",
        "technical support",
        "mortgage applications",
        "credit card statements",
        "electricity bill payments",
        "college tuition fees",
        "vehicle insurance",
        "foreign currency exchange",
        "cryptocurrency trading",
        "mutual fund returns",
        "travel insurance"
    ]
    
    generic_queries = [
        "Can you help me with my finances?",
        "Tell me more about investments.",
        "How to handle bad customer service?",
        "What should I do to save money?",
        "Why should I trust you?",
        "Can you tell me how to invest in mutual funds?",
        "What are the benefits of using a bank instead of LIC?",
        "How to get a home loan quickly?",
        "Why is my internet slow?",
        "Can I use my policy for buying property?",
    ]
    
    negative_queries = generic_queries.copy()

    # Paraphrase positive queries with irrelevant contexts
    for _ in range(num_queries - len(generic_queries)):
        query = random.choice(positive_queries)
        context = random.choice(irrelevant_contexts)
        if "policy" in query:
            modified_query = query.replace("policy", context)
        else:
            modified_query = f"{query} related to {context}"
        negative_queries.append(modified_query)
    
    return negative_queries


if __name__ == "__main__":
    # Load positive queries from the provided file
    file_path = "/mnt/data/LIC_qeries.txt"
    with open(file_path, "r") as file:
        positive_queries = [line.strip() for line in file.readlines()]

    # Generate 100 negative queries
    negative_queries = generate_negative_queries(positive_queries, num_queries=100)

    # Save to a file for reference
    output_file = "/mnt/data/negative_queries.txt"
    with open(output_file, "w") as file:
        file.write("\n".join(negative_queries))
