import os
import pdfplumber
from transformers import pipeline

# 1. Extract text from PDF
def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extracts text from a given PDF file using pdfplumber.
    """
    document_text = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            document_text += page.extract_text() + "\n"
    
    return document_text

# 2. Split text into smaller chunks for processing
def split_text_into_chunks(text: str, chunk_size: int = 500) -> list:
    """
    Split the document text into smaller chunks for processing.
    """
    chunks = []
    words = text.split()  # Split by words
    current_chunk = []
    
    for word in words:
        if len(" ".join(current_chunk)) + len(word) <= chunk_size:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
    
    # Add the last chunk if any
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

# 3. Generate questions and answers for each chunk of text using Hugging Face's transformers pipeline
def generate_questions_and_answers(chunks: list) -> list:
    """
    Generate questions and answers for each chunk of text using a Q&A model.
    """
    #model_path = os.path.expanduser("~/.cache/huggingface/hub/models--google--flan-t5-large/")  # Local path
    qa_model = pipeline("text2text-generation", model="google/flan-t5-large")
    qna_pairs = []
    
    for chunk in chunks:
        # Generate one question (no need for num_return_sequences or beam search)
        question_prompt = f"Generate a single question based on the following context:\n{chunk}"
        question_result = qa_model(question_prompt, max_length=100)  # Returns one result
        question = question_result[0]["generated_text"]  # Extract the generated question
        
        # Generate one answer for the generated question
        answer_prompt = f"Provide an answer for the question: '{question}' based on this context:\n{chunk}"
        answer_result = qa_model(answer_prompt, max_length=100)  # Returns one result
        answer = answer_result[0]["generated_text"]  # Extract the generated answer
        
        # Append the question and answer pair to the list
        qna_pairs.append({"question": question, "answer": answer})

    return qna_pairs


# 4. Save the generated questions and answers into separate files
def save_qna_to_files(qna_pairs, question_file: str, answer_file: str):
    """
    Save the generated questions and answers to separate text files.
    """
    with open(question_file, "w", encoding="utf-8") as q_file, open(answer_file, "w", encoding="utf-8") as a_file:
        for pair in qna_pairs:
            q_file.write(pair["question"] + "\n")
            a_file.write(pair["answer"] + "\n")

# 5. Full processing pipeline
def process_pdf_and_generate_qna(pdf_path: str, question_file: str, answer_file: str):
    """
    Full process of extracting text from a PDF, generating Q&A, and saving them to files.
    """
    print(f"Processing PDF: {pdf_path}")
    
    # Step 1: Extract text from PDF
    document_text = extract_text_from_pdf(pdf_path)
    
    # Step 2: Split extracted text into chunks
    text_chunks = split_text_into_chunks(document_text)
    print(f"Extracted {len(text_chunks)} chunks of text.")
    
    # Step 3: Generate questions and answers for each chunk
    qna_pairs = generate_questions_and_answers(text_chunks)
    print(f"Generated {len(qna_pairs)} Q&A pairs.")
    
    # Step 4: Save the Q&A pairs to files
    save_qna_to_files(qna_pairs, question_file, answer_file)
    print(f"Q&A saved to {question_file} and {answer_file}.")

# 6. Usage example
if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script directory
    # Fix PDF path to be relative to the script directory
    pdf_path = os.path.join(script_dir, '..', 'data', 'client1', '1.pdf')  # Construct relative path
    pdf_path = os.path.normpath(pdf_path)  # Normalize path
    print(f"PDF Path: {pdf_path}")
    
    # Define output files for questions and answers
    question_file = "questions.txt"
    answer_file = "answers.txt"
    
    # Process PDF and generate questions and answers
    process_pdf_and_generate_qna(pdf_path, question_file, answer_file)
