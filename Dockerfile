# Use Python 3.11 slim image
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Copy requirements.txt from project root
COPY requirements.txt /app/requirements.txt

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    poppler-utils \
    libpoppler-dev \
    pkg-config \
    libjpeg-dev \
    zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel \
 && pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch \
 && pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the project files
COPY . /app

# Let Hugging Face/host decide the port
ENV PORT=7860
EXPOSE 7860

# Run FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--loop", "asyncio", "--ws", "websockets"]
