#!/bin/bash

echo "Starting FastAPI Backend..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Wait for backend to start
sleep 5

echo "Starting Streamlit Frontend..."
streamlit run frontend/streamlit/app.py --server.port 7860 --server.address 0.0.0.0
