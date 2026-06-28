# agents/ocr_agent.py
import easyocr
import fitz  # PyMuPDF (PDF read karne ke liye)
import os

# EasyOCR ka reader initialize karna ('en' matlab English)
# Note: gpu=False rakha hai taaki bina graphic card ke bhi chal sake
reader = easyocr.Reader(['en'], gpu=False)

def extract_text_from_image(image_path: str) -> str:
    """Image se text extract karne ka function"""
    try:
        # EasyOCR text read karta hai
        results = reader.readtext(image_path)
        # Saare extracted lines ko ek string mein jodna
        text = "\n".join([res[1] for res in results])
        return text
    except Exception as e:
        return f"Error reading image: {e}"

def extract_text_from_pdf(pdf_path: str) -> str:
    """PDF se text extract karne ka function"""
    try:
        text = ""
        # PyMuPDF se file open karna
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text()
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