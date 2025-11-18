# DOC-IA

Intelligent document extraction platform built with FastAPI, Celery and React.

## Features

- Multi-format ingestion (PDF, scanned images, DOCX, TXT) with full-document text extraction via PyMuPDF, python-docx and Tesseract OCR (fra + eng)
- Gemini Pro–powered field extraction with heuristic boosts for document type & confidence, plus manual review/edit UI
- FastAPI + PostgreSQL backend with async CRUD, pagination, filtering and CSV/JSON/XLS exports
- Celery workers + Redis queues for background processing, upload-to-extraction pipelines, and task status tracking
- React (Vite + Tailwind) dashboard for uploads, previewing full text, editing extracted JSON, and triggering exports
- Docker Compose stack (backend, worker, Postgres, Redis, frontend) for easy local deployment

## Getting Started

```bash
cp backend/.env.example backend/.env
docker compose up --build
```

Access backend docs at `http://localhost:8000/docs` and frontend at `http://localhost:5173`.

## Architecture

```
docker-compose
├─ backend (FastAPI + Celery)
│  ├─ core (config, db, security)
│  ├─ api/v1 (upload, documents, export, tasks)
│  ├─ services (text extraction, Gemini, storage, task tracking)
│  ├─ workers (Celery tasks)
│  └─ models/schemas (SQLAlchemy + Pydantic)
├─ frontend (React + Vite + Tailwind)
│  ├─ components (UploadZone, DocumentList, DocumentViewer)
│  ├─ services (axios client)
│  └─ types
├─ postgres
└─ redis
```

## Testing

Run backend tests:

```bash
cd backend && pytest
```
