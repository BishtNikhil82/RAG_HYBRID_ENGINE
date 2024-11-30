from fastapi import FastAPI, HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from audio_assistant.conversion import transcribe_audio,text_to_speech_gtts
from fastapi.responses import FileResponse
import os

app = FastAPI()
# Allowable origins for CORS
origins = [
    "http://127.0.0.1:5001",  # Frontend running locally
    "http://localhost:5001", # Alternative localhost frontend
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Temporary directory for storing audio files
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)
@app.post("/audio-to-text")
async def audio_query(request: Request):
    """
    Handle a query where audio data is sent in the POST payload as binary.
    """
    try:
        # Step 1: Read the audio data from the request body
        audio_data = await request.body()
        if not audio_data:
            raise HTTPException(status_code=400, detail="No audio data provided in the request.")

        # Step 2: Save audio data to a temporary file
        temp_audio_path = os.path.join(TEMP_DIR, "input_audio.m4a")
        with open(temp_audio_path, "wb") as temp_audio_file:
            temp_audio_file.write(audio_data)

        # Step 3: Convert audio to text
        transcribed_text = transcribe_audio(temp_audio_path)  # Implement or call your transcription function
        if not transcribed_text:
            raise HTTPException(status_code=500, detail="Failed to transcribe the audio.")

        print(f"Transcribed text: {transcribed_text}")

        return transcribed_text
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        # Generic error handling
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/text-to-audio")
async def text_query(request: Request):
    try:
        # Step 1: Read the JSON data from the request body
        body = await request.json()
        text_data = body.get("query")
        
        if not text_data:
            raise HTTPException(status_code=400, detail="No text data provided in the request.")
        
        # Step 6: Convert response text back to audio
        audio_response_path = os.path.join(TEMP_DIR, "response_audio.mp3")
        text_to_speech_gtts(text_data, audio_response_path)  # Call your TTS function
        
        # Step 7: Return the audio response
        return FileResponse(
            audio_response_path,
            media_type="audio/mpeg",
            filename="response_audio.mp3"
        )

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        # Generic error handling
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
