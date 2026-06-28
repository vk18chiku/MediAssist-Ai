# agents/symptom_agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# .env se API keys load karna
load_dotenv()

# OpenAI ka LLM initialize karna (temperature 0.3 rakha hai taaki AI zyada creative na ho aur factual rahe)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.3)

def run_symptom_checker(symptoms: str) -> str:
    """
    Yeh function symptoms input leta hai aur OpenAI se possible causes nikal kar deta hai.
    """
    # AI ke liye strict instructions set karna
    prompt = ChatPromptTemplate.from_messages([
        (
            "system", 
            "You are a helpful and responsible medical AI assistant. "
            "Given a list of symptoms, provide a few possible common causes. "
            "Use clear bullet points. "
            "CRITICAL RULE: ALWAYS include a strong disclaimer at the end stating that you are an AI, "
            "this is not medical advice, and the user MUST consult a real doctor for an accurate diagnosis."
        ),
        ("user", "Symptoms: {symptoms}")
    ])

    # Chain banana (Prompt -> LLM)
    chain = prompt | llm
    
    # AI ko run karna
    response = chain.invoke({"symptoms": symptoms})
    return response.content

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