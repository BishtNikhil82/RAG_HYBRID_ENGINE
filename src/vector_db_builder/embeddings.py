from langchain.embeddings import SentenceTransformerEmbeddings

def get_embedding_model(config_dct):
    embedding_model_name = config_dct["embedding_model"]
    embedding_model = SentenceTransformerEmbeddings(model_name=embedding_model_name)
    return embedding_model
