from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

def get_prompt():
    # Refined RAG chain-specific prompt with concise instructions
    template = """
    Answer the user's question based solely on the provided context. Ensure your response is accurate, concise, and grammatically correct. Do not exceed 100 words, and avoid including any information that is not explicitly mentioned in the context.

    Context:
    {context}

    Question:
    {question}

    Answer (maximum 50 words):
    """
    return ChatPromptTemplate.from_template(template)

# def get_prompt():
#     template = """
#     Based on the provided context, determine the user's score and provide a detailed explanation for the score.

#     - The score should be a value between 0 and 100.
#     - Provide a detailed reasoning for the score.

#     Context:
#     {context}

#     Question:
#     {question}

#     Answer:
#     Score: {{value between 0 and 100}}
#     Reasoning: {{detailed reasoning for the score}}
#     """
#     return ChatPromptTemplate.from_template(template)



