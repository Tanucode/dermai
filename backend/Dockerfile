# Use official Python 3.10 slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for compiling some Python packages)
# libgl1 and libglib2 are needed for OpenCV on Linux
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Hugging Face Spaces requires port 7860
EXPOSE 7860

# Start FastAPI using Uvicorn on port 7860 (HF Spaces requirement)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
