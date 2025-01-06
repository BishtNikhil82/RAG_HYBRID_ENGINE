from transformers import pipeline
from PIL import Image
import os
import numpy as np

from transformers import pipeline
from PIL import Image

# pipe = pipeline("document-question-answering", model="naver-clova-ix/donut-base-finetuned-docvqa")

# question = "What is the purchase amount?"
# image = Image.open("your-document.png")

# pipe(image=image, question=question)

# ## [{'answer': '20,000$'}]


def answer_question_on_image(image_path, question):

        # Load the model
        #document_qa_pipeline = pipeline("document-question-answering", model="impira/layoutlm-document-qa")
        document_qa_pipeline = pipeline("document-question-answering", model="naver-clova-ix/donut-base-finetuned-docvqa")

        # Load and preprocess the image
        image = Image.open(image_path)
        # Pass the image and question to the pipeline
        result = document_qa_pipeline({"image": image, "question": question})
        return result


if __name__ == "__main__":

    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script directory
    image_path = os.path.join(script_dir, '..', 'data', 'client1', '4.png')  # Construct relative path
    image_path = os.path.normpath(image_path)  # Normalize path
    print(f"PDF Path: {image_path}")
    # Path to the document image
    # image_path = "path_to_your_image.jpg"  # Replace with your image path
    
    # Question to ask about the document
    question = "What is basic sum assured"
    
    # Get the answer
    try:
        answer = answer_question_on_image(image_path, question)
        print("Answer:", answer)
    except Exception as e:
        print(f"Error: {e}")
