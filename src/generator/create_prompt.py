from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def get_prompt():
    # RAG chain-specific prompt with a word limit
    template = """
    You are an LIC policy expert. Use the context provided below to answer the user's question accurately and concisely. Ensure your response is limited to 200 words and relies only on the context provided. Do not include information outside the given context.

    Context:
    {context}

    Question: {question}

    Answer (maximum 200 words):
    """
    return ChatPromptTemplate.from_template(template)

