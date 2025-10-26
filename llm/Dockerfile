FROM python:3.11-slim

RUN apt-get update && apt-get install -y build-essential curl

WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Create models directory
RUN mkdir -p /app/models

COPY main.py main.py
# Copy the local GGUF model file
# Place your tinyllama GGUF file in the llm/ directory and update the filename below
COPY tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf /app/models/tinyllama.gguf

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]