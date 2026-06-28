# agents/report_summarizer_agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import sys
import os
# Project root ko path mein add kar rahe hain taaki 'agents' package mil sake
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set stdout to utf-8 to support emoji printing on Windows
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Humara banaya hua OCR agent import kar rahe hain
from agents.ocr_agent import run_ocr_agent

load_dotenv()

# AI LLM initialize karna
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

def summarize_report(file_path: str) -> str:
    """
    Yeh function pehle OCR se text nikalta hai, fir AI se summary banwata hai.
    """
    print(f"📄 Step 1: '{file_path}' se text nikal rahe hain (OCR)...")
    ocr_result = run_ocr_agent(file_path)
    
    extracted_text = ocr_result.get("extracted_text", "")
    error = ocr_result.get("error", "")
    
    if error or not extracted_text.strip():
        return f"Error: Text nahi padh paye. Detail: {error or 'No text found.'}"

    print("🧠 Step 2: AI Report samajh raha hai aur summary bana raha hai...\n")
    
    # AI ke liye Instructions
    prompt = ChatPromptTemplate.from_messages([
        (
            "system", 
            "You are an expert medical AI assistant. Your job is to read the extracted text from a medical report "
            "(like a blood test, MRI report, etc.) and provide a simple, easy-to-understand summary for the patient. "
            "Highlight any abnormal values or areas of concern. "
            "IMPORTANT: Always add a disclaimer at the end that this is AI-generated and they MUST consult a real doctor."
        ),
        ("user", "Here is the medical report text:\n\n{report_text}")
    ])

    # Chain banana (Prompt -> LLM)
    chain = prompt | llm
    
    # AI ko extract kiya hua text bhejna
    response = chain.invoke({"report_text": extracted_text})
    return response.content

# Testing Block
if __name__ == "__main__":
    print("📊 Report Summarizer Test Start...\n")
    
    # Wahi test image jo aapne Phase 3 mein use ki thi
    test_file = "test_report.jpg" 
    
    if os.path.exists(test_file):
        final_summary = summarize_report(test_file)
        
        print("\n" + "="*50)
        print("📝 AI REPORT SUMMARY")
        print("="*50)
        print(final_summary)
        print("="*50)
    else:
        print(f"❌ '{test_file}' folder mein nahi mili.")