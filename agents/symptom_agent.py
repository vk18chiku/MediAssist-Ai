# agents/symptom_agent.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix Windows console encoding for emojis
if getattr(sys.stdout, 'encoding', None) and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

import re
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from backend.database.connection import engine
from sqlalchemy.orm import sessionmaker
from backend.database.models import User, Doctor

# Database Session Setup
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# .env se API keys load karna
load_dotenv()

# OpenAI ka LLM initialize karna (temperature 0.3 rakha hai taaki AI zyada creative na ho aur factual rahe)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

def get_doctors_by_specialization(specialization: str):
    db = SessionLocal()
    is_fallback = False
    try:
        # Pura naam match karne ke bajaye keywords check karenge
        # "Cardiologist", "Orthopedic", etc.
        doctors = db.query(User.name, Doctor.specialization, Doctor.experience)\
                    .join(Doctor, User.id == Doctor.user_id)\
                    .filter(Doctor.specialization.ilike(f"%{specialization}%")).all()
        
        # Agar koi specialist nahi mila, to "General Physician" recommend karenge
        if not doctors:
            doctors = db.query(User.name, Doctor.specialization, Doctor.experience)\
                        .join(Doctor, User.id == Doctor.user_id)\
                        .filter(Doctor.specialization.ilike("%General Physician%")).all()
            is_fallback = True
            
        return doctors, is_fallback
    finally:
        db.close()

def run_symptom_checker(symptoms: str, needs_recommendation: bool = False) -> str:
    """
    Yeh function symptoms input leta hai aur OpenAI se possible causes nikal kar deta hai.
    Sath hi recommended doctor aur available doctors ki list deta hai.
    """
    if needs_recommendation:
        rule_2 = (
            "CRITICAL RULE 2: Because the user explicitly asked for a doctor recommendation, KEEP YOUR MEDICAL EXPLANATION EXTREMELY BRIEF (just 1 or 2 sentences max) and do NOT write a long detailed list of causes. Then, at the very end of your entire response, output EXACTLY this format on a new line: 'RECOMMENDED_SPECIALIST: [Specialization]', "
            "where [Specialization] is ONE specific type of doctor best suited for this (e.g., General Physician, Cardiologist, Orthopedic, Pediatrician, Dermatologist)."
        )
    else:
        rule_2 = "Do NOT recommend any specific doctor or output 'RECOMMENDED_SPECIALIST'."

    prompt = ChatPromptTemplate.from_messages([
        (
            "system", 
            "You are an empathetic, helpful, and responsible medical AI assistant. "
            "Given a list of symptoms or a medical condition, provide a detailed, easy-to-understand explanation of possible common causes. "
            "Use clear bullet points and keep a comforting tone. "
            "CRITICAL RULE 1: ALWAYS include a strong disclaimer at the end stating that you are an AI, "
            f"this is not medical advice, and the user MUST consult a real doctor for an accurate diagnosis.\n{rule_2}"
        ),
        ("user", "Symptoms/Query: {symptoms}")
    ])

    chain = prompt | llm
    response_text = chain.invoke({"symptoms": symptoms}).content
    
    final_response = response_text

    specialization_match = re.search(r'RECOMMENDED_SPECIALIST:\s*(.*)', response_text)
    if specialization_match:
        specialization = specialization_match.group(1).strip()
        # Clean up markdown like **Cardiologist** or Trailing period Cardiologist.
        specialization = re.sub(r'[*.]', '', specialization).strip()
        
        final_response = re.sub(r'RECOMMENDED_SPECIALIST:\s*.*', '', response_text).strip()
        
        doctors, is_fallback = get_doctors_by_specialization(specialization)
        
        final_response += f"\n\n**Required Specialist:** {specialization}\n"
        
        if doctors:
            if is_fallback:
                final_response += f"\n⚠️ *No {specialization}s available. Recommending General Physicians:*\n\n"
            else:
                final_response += f"\n**Available {specialization}s:**\n"
            for doc in doctors:
                exp = doc.experience if doc.experience else 0
                doc_name = doc.name.replace('Dr. ', '').replace('Dr ', '')
                # Mock rating if none exists
                rating = 4.8
                final_response += f"• **Dr. {doc_name}**\n⭐ {rating}\n{exp} Years Experience\n\n"
            
            final_response += "\n**Which doctor would you like to book an appointment with?**"
        else:
            final_response += "\n❌ *No doctors of this specialization are currently available in our system.*"

    return final_response

# Agar hum is file ko directly run karein, to yeh testing ke kaam aayega
if __name__ == "__main__":
    print("🤖 Symptom Checker Agent Test Start...\n")
    
    test_symptoms = "I have a mild fever, headache, and body ache for the last 2 days."
    print(f"Patient: {test_symptoms}\n")
    
    try:
        result = run_symptom_checker(test_symptoms)
        print("AI Doctor Response:")
        print("-" * 40)
        print(result)
        print("-" * 40)
    except Exception as e:
        print(f"Error: {e}")
        print("\nTip: Check if OPENAI_API_KEY is correct in your .env file!")