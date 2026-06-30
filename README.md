---
title: MediAssist AI
emoji: 🏥
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# 🩺 MediAssist AI

MediAssist AI is an advanced, AI-powered healthcare companion designed to bridge the gap between patients and medical information. Featuring a sleek, ChatGPT-inspired Dark Mode UI, it offers a seamless and intuitive experience for users to manage their health.

![MediAssist AI Banner](https://img.shields.io/badge/MediAssist-AI%20Healthcare-blue?style=for-the-badge&logo=health)

## ✨ Key Features

*   **🗣️ Voice Mode Integration:** Talk directly to the AI using the built-in microphone for a hands-free, interactive conversational experience.
*   **🤖 Multi-Agent Architecture:** Powered by specialized LangGraph AI Agents:
    *   **RAG Agent:** Provides accurate symptom checking and medicine information using medical databases.
    *   **SQL Agent:** Handles doctor discovery, directory filtering, and appointment booking seamlessly.
    *   **OCR Agent:** Upload medical reports (PDF/Images) and get instant, easy-to-understand summaries.
*   **💬 Premium Chat Interface:** A sleek, dark-pill shaped chat interface tailored for optimal user experience, complete with dynamic chat histories.
*   **🔐 Secure Authentication:** OTP-based email verification for safe and secure user and doctor registration/login.
*   **👨‍⚕️ Doctor Directory:** Find specialists, view doctor profiles (with avatars), and manage appointments efficiently.
*   **📜 Session Management:** Save, resume, or delete your past health consultations anytime.

## 🛠️ Technology Stack

*   **Frontend:** Streamlit (Customized CSS & JS for premium UI), Streamlit Mic Recorder
*   **Backend:** FastAPI, Python, SQLAlchemy, JWT Authentication
*   **AI & LLMs:** LangChain, LangGraph, Groq API (LLaMA3), Google Generative AI (Gemini for OCR)
*   **Database:** SQLite (Relational DB for users, doctors, chats, and appointments)
*   **Infrastructure:** Docker & Docker Compose for rapid, containerized deployment

## 🚀 Getting Started

### Prerequisites
*   [Docker](https://www.docker.com/products/docker-desktop/) & Docker Compose
*   [Python 3.10+](https://www.python.org/downloads/) (For local development)

### Environment Variables
Create a `.env` file in the root directory and add your API keys:
```env
GROQ_API_KEY=your_groq_api_key
GEMINI_API_KEY=your_gemini_api_key
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
```

### Run with Docker (Recommended)
Simply start the services using Docker Compose:
```bash
docker-compose up --build -d
```
*   **Frontend (Streamlit):** Available at `http://localhost:8501`
*   **Backend (FastAPI):** Available at `http://localhost:8000`

### Run Locally (Without Docker)
1. **Start the Backend:**
    ```bash
    cd backend
    pip install -r requirements.txt
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
2. **Start the Frontend:**
    ```bash
    cd frontend/streamlit
    pip install -r requirements.txt
    streamlit run app.py
    ```

## 📂 Project Structure

```
MediAssist/
├── backend/
│   ├── main.py              # FastAPI application & API endpoints
│   ├── models.py            # SQLAlchemy database models
│   ├── ai_agents.py         # LangGraph agents (RAG, SQL, General, OCR)
│   ├── email_service.py     # OTP generation and email dispatch
│   └── requirements.txt
├── frontend/
│   └── streamlit/
│       ├── app.py           # Streamlit UI & customized ChatGPT-style chat
│       └── requirements.txt
├── docker-compose.yml       # Container orchestration
└── README.md
```

## 🤝 Contributing
Contributions are always welcome! Feel free to open an issue or submit a Pull Request if you have suggestions for improvements.

## 📜 License
This project is licensed under the MIT License.
