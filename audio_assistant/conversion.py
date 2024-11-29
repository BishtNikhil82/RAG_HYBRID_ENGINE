import whisper
import ffmpeg
import pyttsx3
from gtts import gTTS
from pydub import AudioSegment
from io import BytesIO
import os

print(whisper.__file__)

# Function to convert AAC to WAV
def convert_aac_to_wav(aac_file, wav_file):
    try:
        ffmpeg.input(aac_file).output(wav_file, format='wav').run(overwrite_output=True)
        print(f"Converted {aac_file} to {wav_file}")
        return wav_file
    except Exception as e:
        print(f"Error converting file: {e}")
        return None


def convert_m4a_to_wav(m4a_file, wav_file):
    try:
        # Use ffmpeg to convert M4A to WAV
        ffmpeg.input(m4a_file).output(wav_file, format='wav').run(overwrite_output=True)
        print(f"Converted {m4a_file} to {wav_file}")
        return wav_file
    except Exception as e:
        print(f"Error converting file: {e}")
        return None


def transcribe_audio(file_path):
    try:
        # Load the Whisper model
        model = whisper.load_model("base")  # You can use "tiny", "base", "small", "medium", or "large"

        # Detect language
        audio = whisper.load_audio(file_path)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(model.device)
        _, probs = model.detect_language(mel)
        detected_language = max(probs, key=probs.get)
        print(f"Detected Language: {detected_language}")

        # Transcribe the audio file
        result = model.transcribe(file_path)
        print("Transcription completed!")
        return result["text"]

    except Exception as e:
        print(f"Error during transcription: {e}")
        return None


# Speech-to-Text Functionality
def speech_to_text(aac_file):
    wav_file = "temp_output.wav"

    # Step 1: Convert AAC to WAV
    #converted_file = convert_aac_to_wav(aac_file, wav_file)
    # script_dir = os.path.dirname(os.path.abspath(__file__))
    # whisper_dir = os.path.join(script_dir)
    # m4a_file = os.path.join(whisper_dir, "input.m4a")
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    whisper_dir = os.path.join(script_dir)
    # Ensure the whisper directory exists
    if not os.path.exists(whisper_dir):
        os.makedirs(whisper_dir)  # Create directory if it doesn't exist
    # Define the output file path
    m4a_file = os.path.join(whisper_dir, "input.m4a")
    #m4a_file = "input.m4a"
    converted_file = convert_m4a_to_wav(m4a_file, wav_file)
    if not converted_file:
        print("Failed to convert the file.")
        return None

    # Step 2: Transcribe audio
    transcription = transcribe_audio(converted_file)
    if transcription:
        print("\n=== Transcription ===")
        print(transcription)
        print("======================")
    else:
        print("Transcription failed.")

    # Clean up temporary WAV file
    if os.path.exists(wav_file):
        os.remove(wav_file)

    return transcription

# Text-to-Speech Functionality
def text_to_speech_offline(text, audio_response_path):
    try:
        # Initialize the text-to-speech engine
        engine = pyttsx3.init()

        # Adjust speech rate for clarity
        rate = engine.getProperty('rate')
        print(f"Default speech rate: {rate}")
        engine.setProperty('rate', 150)  # Adjust to desired speed (lower = slower)

        # Set volume (default is 1.0)
        volume = engine.getProperty('volume')
        print(f"Default volume: {volume}")
        engine.setProperty('volume', 0.9)  # Set volume level (0.0 to 1.0)

        # Select a female voice
        voices = engine.getProperty('voices')
        female_voice_found = False
        for voice in voices:
            if "female" in voice.name.lower():  # Attempt to find a female voice
                engine.setProperty('voice', voice.id)
                print(f"Selected voice: {voice.name}")
                female_voice_found = True
                break

        if not female_voice_found:  # Fallback if no female voice found
            print("No female voice found, using default voice.")

        # Convert text to speech and save to a file
        print("Converting text to speech...")
        engine.save_to_file(text, audio_response_path)
        engine.runAndWait()
        print(f"Audio saved as {audio_response_path}")
    except Exception as e:
        print(f"Error during text-to-speech: {e}")



# def text_to_speech_coqui(text, audio_response_path):
#     try:
#         # Load a pre-trained TTS model
#         tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=False)

#         # Convert text to audio and save to file
#         print("Converting text to speech using Coqui TTS...")
#         tts.tts_to_file(text=text, file_path=audio_response_path)
#         print(f"Audio saved as {audio_response_path}")
#     except Exception as e:
#         print(f"Error during Coqui TTS: {e}")

def split_text(text, max_length=80):
    """Split text into chunks of max_length characters."""
    paragraphs = []
    while len(text) > max_length:
        split_point = text[:max_length].rfind(".")  # Find the last sentence boundary
        if split_point == -1:
            split_point = max_length
        paragraphs.append(text[:split_point + 1].strip())
        text = text[split_point + 1:]
    paragraphs.append(text.strip())
    return paragraphs

def text_to_speech_gtts(text, audio_response_path):
    try:
        print("Splitting text into chunks...")
        chunks = split_text(text)

        combined_audio = AudioSegment.empty()  # Initialize an empty AudioSegment

        for i, chunk in enumerate(chunks):
            print(f"Processing chunk {i + 1}/{len(chunks)}")
            
            # Generate TTS audio and save it to a BytesIO buffer
            tts = gTTS(chunk, lang='en')
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)

            # Load the audio chunk into pydub and append to the combined audio
            chunk_audio = AudioSegment.from_file(audio_buffer, format="mp3")
            combined_audio += chunk_audio
            print(f"Chunk {i + 1} added to combined audio")

        # Export the final combined audio to the specified file
        combined_audio.export(audio_response_path, format="mp3")
        print(f"Final audio saved as {audio_response_path}")

    except Exception as e:
        print(f"Error during text-to-speech: {e}")


# Example usage for testing
# if __name__ == "__main__":
#     long_text = """
#     Artificial Intelligence (AI) is one of the most transformative technologies of our time. It is increasingly being 
#     integrated into various sectors, including healthcare, finance, transportation, education, and entertainment. AI 
#     systems, such as machine learning and natural language processing, are capable of analyzing vast amounts of data, 
#     identifying patterns, and making predictions with remarkable accuracy. In healthcare, AI is being used to assist 
#     in diagnostics, drug discovery, and personalized medicine. For instance, AI-powered algorithms can analyze medical 
#     images to detect diseases like cancer at an early stage. In the financial industry, AI is improving fraud detection, 
#     automating trading processes, and enhancing customer service through chatbots. Autonomous vehicles, powered by AI, 
#     are set to revolutionize transportation by reducing accidents caused by human error. Similarly, AI-driven tools 
#     are personalizing learning experiences for students, making education more accessible and efficient. Despite its 
#     numerous benefits, AI also poses challenges such as ethical concerns, job displacement, and the need for robust 
#     regulatory frameworks. It is essential to address these issues responsibly to ensure that AI serves as a force for 
#     good in society. As the technology continues to evolve, it will undoubtedly shape the future in ways we can only 
#     begin to imagine.
#     """
#     output_file = "response_audio.mp3"
#     text_to_speech_gtts(long_text, output_file)



# # Case Selection Function
# def main():
#     while True:
#         print("\nChoose an option:")
#         print("1. Transcribe an AAC audio file to text (Speech-to-Text).")
#         print("2. Convert text to speech (Text-to-Speech).")
#         print("3. Exit.")
#         choice = input("Enter your choice (1/2/3): ").strip()

#         if choice == "1":
#             aac_file = input("Enter the path to your AAC audio file: ").strip()
#             transcription = speech_to_text(aac_file)
#             if transcription:
#                 save_option = input("Do you want to save the transcription to a file? (yes/no): ").lower()
#                 if save_option == "yes":
#                     with open("transcription.txt", "w") as f:
#                         f.write(transcription)
#                     print("Transcription saved to 'transcription.txt'.")
#         elif choice == "2":
#             text = input("Enter the text you want to convert to speech: ").strip()
#             if text:
#                 #text_to_speech(text)
#                 text_to_speech_gtts(text)
#             else:
#                 print("No text entered. Please try again.")
#         elif choice == "3":
#             print("Exiting...")
#             break
#         else:
#             print("Invalid choice. Please try again.")

# # Run the program
# if __name__ == "__main__":
#     main()
