# rag/ingest.py
import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# .env file se keys load karna
load_dotenv()

# ChromaDB kahan save hoga, uska rasta
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./vector_db/chroma_store")

def ingest_medical_docs(directory: str = "medical_docs"):
    print(f"📂 '{directory}' folder se PDFs dhundh rahe hain...")
    
    # Agar folder nahi hai to bana do
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"❌ Folder '{directory}' nahi tha, toh naya bana diya hai.")
        print("👉 Please isme koi Medical PDF daalein aur dubara run karein.")
        return

    # Folder se saare PDFs load karna
    loader = PyPDFDirectoryLoader(directory)
    documents = loader.load()

    if not documents:
        print("⚠️ Koi PDF nahi mili! Please 'medical_docs' folder mein PDF daalein.")
        return

    print(f"✂️ {len(documents)} pages load hue. Ab unhe chhote chunks (hisson) mein kaat rahe hain...")
    
    # Text ko chhote hisson mein kaatna taaki AI easily padh sake
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)

    print("🧠 Embeddings generate kar rahe hain aur ChromaDB mein save kar rahe hain...")
    print("⏳ Isme thoda time lag sakta hai, please wait...")
    
    # OpenAI ka use karke text ko numbers (vectors) mein convert karna
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Data ko ChromaDB mein save karna
    vector_db = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DB_PATH
    )
    
    print("✅ Data successfully ChromaDB vector database mein save ho gaya hai!")

if __name__ == "__main__":
    print("🚀 Ingestion Process Start...\n")
    ingest_medical_docs()