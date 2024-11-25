import cProfile
import pstats
from src.vector_db_builder.chroma import load_chroma_db
from src.generator.rag_chain import get_rag_chain
from config.load_config import load_yaml_config

def profile_rag_workflow():
    """
    Function to profile the RAG workflow:
    1. Load the vector database.
    2. Initialize the RAG chain with the phi3 model.
    3. Execute a query and analyze the response.
    """
    # Load configuration
    config_path = "config/config.yaml"
    config_dct = load_yaml_config(config_path)

    # Load Chroma vector database
    print("Loading Chroma vector database...")
    vectorstore = load_chroma_db(config_dct)

    # Initialize RAG chain
    print("Initializing RAG chain...")
    rag_chain = get_rag_chain(config_dct)

    # Perform a query
    query = "What is the revival period for policies taken on or after 01.01.2014?"
    print(f"Running query: {query}")
    response = rag_chain.invoke(query)
    print("Response:", response)

# Profile the workflow
if __name__ == "__main__":
    profile_output = "rag_workflow_profile.prof"

    # Use cProfile to profile the function
    print(f"Profiling the RAG workflow. Output will be saved to {profile_output}...")
    cProfile.run("profile_rag_workflow()", profile_output)

    # Analyze the profiling data
    print("Profiling complete. Analyzing the results...\n")
    stats = pstats.Stats(profile_output)
    stats.strip_dirs()  # Remove extra path details
    stats.sort_stats("cumulative")  # Sort by cumulative time
    stats.print_stats(20)  # Print the top 20 functions by cumulative time
