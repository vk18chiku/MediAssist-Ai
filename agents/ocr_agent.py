# agents/ocr_agent.py
import os
import base64
from openai import OpenAI
from pypdf import PdfReader
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def encode_image(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_text_from_image(image_path: str) -> str:
    """Image se text extract karne ka function using OpenAI Vision"""
    try:
        base64_image = encode_image(image_path)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a strict OCR machine. Your ONLY job is to extract text from the provided image. Do NOT converse. Do NOT apologize. If there is no text in the image, output EXACTLY the string 'NO_TEXT_FOUND'."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all the text from this image exactly as it appears."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ]
        )
        extracted = response.choices[0].message.content
        if "NO_TEXT_FOUND" in extracted:
            return ""
        return extracted
    except Exception as e:
        return f"Error reading image: {e}"

def extract_text_from_pdf(pdf_path: str) -> str:
    """PDF se text extract karne ka function using pypdf"""
    try:
        text = ""
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def run_ocr_agent(file_path: str) -> dict:
    """Main function jo decide karega ki file PDF hai ya Image"""
    if not os.path.exists(file_path):
        return {"error": "File nahi mili!", "extracted_text": ""}

    # File ka extension check karna (jpg, png ya pdf)
    file_ext = file_path.lower().split('.')[-1]
    
    if file_ext in ['jpg', 'jpeg', 'png']:
        print("🖼️ Image detect hui, OCR shuru kar rahe hain...")
        text = extract_text_from_image(file_path)
    elif file_ext == 'pdf':
        print("📄 PDF detect hui, text extract kar rahe hain...")
        text = extract_text_from_pdf(file_path)
    else:
        return {"error": "Unsupported format. Sirf JPG, PNG, ya PDF allow hai.", "extracted_text": ""}

    return {"extracted_text": text}

# Testing block
if __name__ == "__main__":
    print("🔍 OCR Agent Test Start...\n")
    
    # Hum ek dummy file ka naam de rahe hain test karne ke liye
    test_file = "test_report.jpg" 
    
    if os.path.exists(test_file):
        result = run_ocr_agent(test_file)
        print("\n--- Extracted Text ---")
        print(result.get("extracted_text", result.get("error")))
        print("----------------------")
    else:
        print(f"❌ '{test_file}' folder mein nahi mili.")
        print("👉 TEST KARNE KA TARIKA:")
        print("1. Koi bhi text wali image apne project folder (hospital-ai) mein daalein.")
        print("2. Uska naam rename karke 'test_report.jpg' rakh dein.")
        print("3. Fir is script ko wapas run karein.")