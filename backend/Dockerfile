FROM python:3.11-slim as base

WORKDIR /app

RUN apt-get update && apt-get install -y tesseract-ocr libgl1 poppler-utils && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
