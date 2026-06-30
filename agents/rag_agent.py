# agents/rag_agent.py
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

# .env se keys load karna
load_dotenv()

CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./vector_db/chroma_store")

def ask_medical_question(question: str) -> str:
    """
    Yeh function user ka sawal lega, ChromaDB se answer dhoondega, aur AI response dega.
    """
    # 1. Database ko wapas load karna (jo ingest.py ne banaya tha)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = Chroma(persist_directory=CHROMA_DB_PATH, embedding_function=embeddings)
    
    # Retriever banana (jo sabse relevant 3 paragraph dhoondh kar layega)
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    # 2. LLM Model setup karna
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)

    # 3. AI ke liye Prompt (Instructions) banana
    system_prompt = (
        "You are an expert medical AI assistant. First, try to use the provided context (extracted from medical documents) "
        "to answer the user's question accurately. \n"
        "If the context does not contain the answer or is empty, use your vast general medical knowledge to provide a helpful, accurate, and detailed response anyway. Do NOT say you don't have enough information.\n"
        "ALWAYS include a disclaimer that this is AI-generated and not a replacement for professional medical advice.\n\n"
        "Context provided to you:\n{context}"
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # 4. Chain banana (Retriever + LLM)
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)

    # 5. AI ko run karna aur sawal bhejna
    print(f"🔍 ChromaDB mein '{question}' ka jawab dhoondh rahe hain...\n")
    response = rag_chain.invoke({"input": question})
    
    return response["answer"]

# Testing Block
if __name__ == "__main__":
    print("📚 RAG Chatbot Test Start...\n")
    
    # Aapne jo PDF daali thi, uske hisaab se koi sawal puchiye
    # Jaise agar dengue ki PDF thi, toh "What are the symptoms of Dengue?"
    test_question = input("👉 Apna sawal type karein (PDF se related): ")
    
    if test_question:
        answer = ask_medical_question(test_question)
        print("\n" + "="*50)
        print("🤖 AI Doctor (from Book) Response:")
        print("="*50)
        print(answer)
        print("="*50)