# agents/medicine_agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# .env se API keys load karna
load_dotenv()

# LLM initialize karna (temperature 0.2 rakha hai taaki factual aur safe rahe)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

def suggest_medicine(symptom: str) -> str:
    """
    Yeh function user ke symptoms ke basis par OTC (Over-The-Counter) medicine suggest karta hai.
    """
    
    # AI ke liye strict rules (Pharmacy Assistant)
    system_prompt = (
        "You are a helpful and responsible AI pharmacy assistant. "
        "Based on the mild symptoms provided by the user, suggest common Over-The-Counter (OTC) medicines. "
        "For each suggested medicine, provide:\n"
        "1. Name of the medicine\n"
        "2. General dosage guidelines (for adults)\n"
        "3. Common side effects or warnings\n\n"
        "CRITICAL RULES:\n"
        "- NEVER suggest prescription-only medications (like antibiotics or heavy painkillers).\n"
        "- ALWAYS include a strong disclaimer at the end stating that you are an AI, this is not a medical prescription, "
        "and the user MUST consult a doctor or pharmacist before taking any medication."
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "My symptom/condition is: {symptom}"),
    ])

    # Chain banana
    chain = prompt | llm
    
    # AI ko run karna
    print(f"💊 '{symptom}' ke liye OTC medicines dhoondh rahe hain...\n")
    response = chain.invoke({"symptom": symptom})
    
    return response.content

# Testing Block
if __name__ == "__main__":
    print("🏥 Medicine Agent Test Start...\n")
    
    test_symptom = "I have a mild headache and a runny nose."
    print(f"Patient says: {test_symptom}\n")
    
    try:
        answer = suggest_medicine(test_symptom)
        print("="*50)
        print("🤖 AI Pharmacist Response:")
        print("="*50)
        print(answer)
        print("="*50)
    except Exception as e:
        print(f"❌ Error: {e}")