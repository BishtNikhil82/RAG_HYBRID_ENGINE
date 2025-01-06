#from langchain.embeddings import SentenceTransformerEmbeddings
#from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_huggingface import HuggingFaceEmbeddings


def get_embedding_model(config_dct):
    embedding_model_name = config_dct["embedding_model"]
    embedding_model = HuggingFaceEmbeddings(model_name=embedding_model_name)
    return embedding_model
