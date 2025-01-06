from transformers import pipeline
import pdfplumber
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from sklearn.metrics.pairwise import cosine_similarity  # Add this import
import os

from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

# Load T5-small model and tokenizer
model_name = 't5-small'
tokenizer = T5Tokenizer.from_pretrained(model_name,legacy=True)
model = T5ForConditionalGeneration.from_pretrained(model_name)


def resize_image(image, target_size=(800, 800)):
    """
    Resize and ensure the image is in RGB format.
    """
    if image.mode != "RGB":
        image = image.convert("RGB")
    return image.resize(target_size, Image.Resampling.LANCZOS)


# Function to convert PDF to images
def convert_pdf_to_images(pdf_path):
    images = convert_from_path(pdf_path, dpi=400)
    return images

# Function to extract text from image (OCR)
def extract_text_from_image(image):
    text = pytesseract.image_to_string(image)
    return text


def answer_question_on_image(image_path, question, threshold=0.5):
    """
    Process a multi-page PDF, extract text from each page, and answer the given question.
    """
    documentlm_pipeline = pipeline("document-question-answering", model="impira/layoutlm-document-qa")

    images = convert_pdf_to_images(image_path)
    best_answer = None
    highest_score = 0

    for page_number, image in enumerate(images, start=1):
        image = resize_image(image)

        inputs = {"image": image, "question": question}

        try:
            result = documentlm_pipeline(inputs)

            if not result or result[0]["score"] < threshold:
                print(f"Page {page_number}: No confident answer found.")
                continue

            if result[0]["score"] > highest_score:
                highest_score = result[0]["score"]
                best_answer = result[0]["answer"]
                print(f"Page {page_number}: Found an answer with score {highest_score}: {best_answer}")

        except Exception as e:
            print(f"Error processing page {page_number}: {e}")
            continue

    

def extract_text_from_pdf_with_documentlm(pdf_path, question="What are the key details in this document?"):
    """
    Extract text or structured data from a PDF using DocumentLM.
    """
    # Load the Document Question Answering pipeline
    documentlm_pipeline = pipeline("document-question-answering", model="impira/layoutlm-document-qa")
    
    extracted_chunks = []
    
    # Convert PDF to images
    images = convert_pdf_to_images(pdf_path)
    
    for page_number, image in enumerate(images, start=1):
        # Extract text using OCR (if necessary)
        page_text = extract_text_from_image(image)
        
        # Resize or process image to ensure consistency (optional)
        image = resize_image(image)  # Make sure all images are the same size

        # Prepare input for the pipeline
        inputs = {
            "image": image,
            "question": question
        }

        try:
            # Provide both image and question to the DocumentLM pipeline
            result = documentlm_pipeline(inputs)
            
            extracted_chunks.append({
                "page_number": page_number,
                "text": page_text,
                "key_values": result
            })
        except ValueError as e:
            print(f"Error processing page {page_number}: {e}")
    
    return extracted_chunks



def split_text_into_chunks(text, chunk_size=500):
    """
    Splits text into smaller chunks for embedding and indexing.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    
    for word in words:
        if len(" ".join(current_chunk)) + len(word) <= chunk_size:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


def index_text_chunks(chunks):
    """
    Indexes text chunks in FAISS using embeddings.
    """
    # Initialize embedding model
    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks)  # Generate embeddings

    # Initialize FAISS index
    index = faiss.IndexFlatL2(embeddings.shape[1])  # L2 distance
    index.add(np.array(embeddings))  # Add embeddings to FAISS
    
    return index, embeddings, model

def query_index(index, query, model, chunks, top_k=3, similarity_threshold=0.7):
    """
    Queries FAISS index to retrieve the most relevant text chunk, with a threshold for similarity score.
    Returns the chunk with the highest similarity if it exceeds the threshold.
    """
    query_embedding = model.encode([query])
    distances, indices = index.search(np.array(query_embedding), k=top_k)

    results = [{"chunk": chunks[i], "distance": distances[0][j]} for j, i in enumerate(indices[0])]

    # Filter results based on similarity threshold
    results = [result for result in results if result["distance"] >= similarity_threshold]

    # If no results meet the threshold, return None or a message indicating no match
    if not results:
        return {"message": "No relevant answer found."}

    # Sort by the highest score (distance)
    best_result = sorted(results, key=lambda x: x["distance"], reverse=True)[0]

    return best_result


# Function to compute semantic search based on embeddings
def semantic_search(query, text_chunks, model):
    query_embedding = model.encode([query])
    chunk_embeddings = model.encode(text_chunks)

    # Compute cosine similarity between query and each chunk
    similarities = cosine_similarity(query_embedding, chunk_embeddings)

    # Sort the chunks based on similarity scores
    top_k = 3  # number of top results you want
    sorted_indices = np.argsort(similarities[0])[::-1][:top_k]

    # Return the top-k most similar chunks
    results = [{"chunk": text_chunks[i], "similarity": similarities[0][i]} for i in sorted_indices]
    return results

def process_and_query_pdfs(pdf_paths, query, chunk_size=300, top_k=3, similarity_threshold=0.7):
    all_chunks = []
    chunk_to_pdf_mapping = []

    # Process each PDF
    for pdf_path in pdf_paths:
        extracted_data = extract_text_from_pdf_with_documentlm(pdf_path)
        for page in extracted_data:
            chunks = split_text_into_chunks(page["text"], chunk_size)
            all_chunks.extend(chunks)
            chunk_to_pdf_mapping.extend([{"pdf_path": pdf_path, "page_number": page["page_number"]}] * len(chunks))

    # Index text chunks in FAISS
    index, embeddings, model = index_text_chunks(all_chunks)

    # Query the FAISS index
    best_result = query_index(index=index, query=query, model=model, chunks=all_chunks, top_k=top_k, similarity_threshold=similarity_threshold)
    
    # If no result found, print a message
    if "message" in best_result:
        print(best_result["message"])
        return

    # Map results back to their PDFs and pages
    best_result["pdf_info"] = chunk_to_pdf_mapping[all_chunks.index(best_result["chunk"])]
    
    return best_result



def summarize_text(text, max_input_length=512, max_output_length=150):
    # Preprocess the text
    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt", max_length=max_input_length, truncation=True)

    # Generate summary with refined hyperparameters
    summary_ids = model.generate(
        inputs,
        max_length=max_output_length,
        num_beams=6,
        repetition_penalty=2.5,
        early_stopping=True
    )

    # Decode and return the result
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script directory
    pdf_path = os.path.join(script_dir, '..', 'data', 'client1', '1.pdf')  # Construct relative path
    pdf_path = os.path.normpath(pdf_path)  # Normalize path
    print(f"PDF Path: {pdf_path}")
    pdf_files = [pdf_path]
    user_query = "Who  is Policy holder"
    answer_question_on_image(pdf_path,user_query)
    # Define the similarity threshold
    # similarity_threshold = 0.7  # You can adjust this value as needed (0 to 1)

    # best_result = process_and_query_pdfs(pdf_files, user_query, chunk_size=500, top_k=3, similarity_threshold=similarity_threshold)
    # summary = summarize_text(best_result['chunk'])
    # print(f"Summary: {summary}")
    # if best_result:
    #     print(f"Best Answer:")
    #     print(f"PDF: {best_result['pdf_info']['pdf_path']}, Page: {best_result['pdf_info']['page_number']}")
    #     print(f"Chunk: {best_result['chunk']}")
    #     print(f"Distance (similarity score): {best_result['distance']}")

