# graph/workflow.py
import os
import sys
from typing import TypedDict
from dotenv import load_dotenv

# Add the parent directory to sys.path so 'agents' can be found when running this file directly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Fix Windows console encoding for emojis
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# Humare banaye hue saare agents import kar rahe hain
from agents.symptom_agent import run_symptom_checker
from agents.medicine_agent import suggest_medicine
from agents.rag_agent import ask_medical_question
from agents.appointment_agent import book_appointment

load_dotenv()
# Supervisor ke liye LLM (Temperature 0 rakha hai taaki routing ekdum accurate ho)
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

# 1. State Define Karna (Data jo agents ke beech ghumega)
class AgentState(TypedDict):
    user_message: str
    agent_type: str
    response: str

# 2. Supervisor Node (Yeh decide karega kis agent ko bulana hai)
def supervisor_node(state: AgentState):
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Analyze the user's medical query (look at the latest intent in the CONVERSATION HISTORY) and classify it into EXACTLY ONE of these categories:\n"
                   "1. 'symptom' (If asking about symptoms, causes, or how they feel)\n"
                   "2. 'medicine' (If asking for basic OTC medicine or quick remedies)\n"
                   "3. 'appointment' (If asking to book a doctor, find a specialist, or if they are providing appointment details like time or date)\n"
                   "4. 'rag' (If asking general medical knowledge, diet, or guidelines from books)\n"
                   "Respond with ONLY the category word (e.g., symptom, medicine, appointment, rag)."),
        ("human", "{user_message}")
    ])
    chain = prompt | llm
    category = chain.invoke({"user_message": state["user_message"]}).content.strip().lower()
    
    # Fallback agar AI ne kuch ajeeb output diya
    if category not in ["symptom", "medicine", "appointment", "rag"]:
        category = "rag" 
        
    return {"agent_type": category}

# 3. Execution Nodes (Jo actual agents ko run karenge)
def symptom_node(state: AgentState):
    return {"response": run_symptom_checker(state["user_message"])}

def medicine_node(state: AgentState):
    return {"response": suggest_medicine(state["user_message"])}

def appointment_node(state: AgentState):
    return book_appointment(state)

def rag_node(state: AgentState):
    return {"response": ask_medical_question(state["user_message"])}

# 4. LangGraph Workflow Build Karna
workflow = StateGraph(AgentState)

# Saare nodes (steps) add karna
workflow.add_node("supervisor", supervisor_node)
workflow.add_node("symptom", symptom_node)
workflow.add_node("medicine", medicine_node)
workflow.add_node("appointment", appointment_node)
workflow.add_node("rag", rag_node)

# Entry point (Sabse pehle message kahan jayega)
workflow.set_entry_point("supervisor")

# Routing Logic (Supervisor ke answer ke basis pe kahan jana hai)
def decide_next(state: AgentState):
    return state["agent_type"]

workflow.add_conditional_edges(
    "supervisor",
    decide_next,
    {
        "symptom": "symptom",
        "medicine": "medicine",
        "appointment": "appointment",
        "rag": "rag"
    }
)

# Har agent apna kaam khatam karke END pe jayega
workflow.add_edge("symptom", END)
workflow.add_edge("medicine", END)
workflow.add_edge("appointment", END)
workflow.add_edge("rag", END)

# Graph ko compile karna
app = workflow.compile()

# Testing Block
if __name__ == "__main__":
    print("🧠 LangGraph Multi-Agent Supervisor Test Start...\n")
    print("Type 'exit' to quit.\n")
    
    while True:
        msg = input("Patient 👤: ")
        if msg.lower() == 'exit':
            break
            
        print("🤖 Supervisor soch raha hai...")
        # Workflow run karna
        result = app.invoke({"user_message": msg})
        
        print("\n" + "="*60)
        print(f"👉 Routed to: [{result['agent_type'].upper()} AGENT]")
        print("="*60)
        print(f"Dr. AI 🩺: {result['response']}\n")