from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate


def get_prompt():
    # Prompt
    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    prompt

    return prompt