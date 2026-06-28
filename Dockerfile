FROM python:3.11-slim

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up user for Hugging Face Spaces (runs as non-root user 1000)
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Copy requirements file and install dependencies
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY --chown=user . .

# Ensure the start script is executable
RUN chmod +x start.sh

# Hugging Face Spaces runs web apps on port 7860 by default
EXPOSE 7860

# Run the start script to launch both FastAPI and Streamlit
CMD ["./start.sh"]
