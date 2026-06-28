# agents/voice_agent.py
import whisper

# Global variable banayenge, par abhi load nahi karenge
model = None

def transcribe_audio(file_path: str):
    global model
    
    # Jab pehli baar koi voice note aayega, sirf tabhi model download/load hoga
    if model is None:
        print("Loading Whisper model... (This might take a minute on first run)")
        model = whisper.load_model("base")
        
    try:
        result = model.transcribe(file_path)
        return {"text": result["text"]}
    except Exception as e:
        return {"error": str(e), "text": "Sorry, failed to process audio."}