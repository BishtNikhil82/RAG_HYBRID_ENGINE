from sentence_transformers import SentenceTransformer
from config.load_config import load_yaml_config

class EmbeddingService:
    def __init__(self, config_path):
        """
        Initializes the EmbeddingService with a SentenceTransformer model.

        Parameters:
        - config_path (str): Path to the configuration YAML file.
        """
        self.config_dct = load_yaml_config(config_path)
        model_name = self.config_dct["embedding_model"]
        self.model = SentenceTransformer(model_name)  # Load the model once during initialization

    def get_embeddings(self, sentences_lst):
        """
        Generates embeddings for a list of sentences.

        Parameters:
        - sentences_lst (list of str): List of sentences to encode.

        Returns:
        - embeddings (ndarray): Embeddings for the input sentences.
        """
        embeddings = self.model.encode(sentences_lst)
        return embeddings


if __name__ == "__main__":
    # Example usage
    sentences = [
        "I need maturity claim requirements.",
        "Do you charge late fee on delayed premium?",
        "How are you?"
    ]
    config_path = "config/config_faq.yaml"
    
    # Initialize the service
    embedding_service = EmbeddingService(config_path)
    
    # Get embeddings for the sentences
    embeddings = embedding_service.get_embeddings(sentences)
    print("Embeddings generated successfully.")
