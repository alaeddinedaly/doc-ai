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

### Environment variables

After copying `backend/.env.example` to `backend/.env`, edit it with your own credentials before launching. The file includes:

```
APP_NAME=DOC-IA
ENVIRONMENT=local
DEBUG=true
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<host>:5432/<database>
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_BACKEND_URL=redis://redis:6379/2
GEMINI_API_KEY=<your_google_generative_ai_key>
GEMINI_MODEL=gemini-pro
ALLOWED_ORIGINS=["http://localhost:5173"]
MAX_UPLOAD_SIZE_MB=50
```

Keep `backend/.env` out of version control (it’s ignored via `.gitignore`) and only commit safe defaults to `backend/.env.example`.

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
