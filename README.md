# Enterprise AI Document Intelligence Platform

An enterprise-grade platform for intelligent document processing, semantic search, and AI-powered question answering with agentic capabilities.

## Features (Milestone 1)

- **Document Upload** — PDF, DOCX, TXT, JPG/PNG with validation
- **Document Management** — CRUD operations with PostgreSQL
- **REST API** — FastAPI with Swagger/OpenAPI documentation
- **Structured Logging** — JSON-formatted logs with request tracing

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI, Pydantic, Uvicorn |
| Database | PostgreSQL 16, SQLAlchemy 2.0, Alembic |
| Logging | structlog |
| Infrastructure | Docker, Docker Compose |

## Quick Start

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git

### Setup

```bash
# Clone and enter project
cd enterprise-ai-platform

# Start PostgreSQL
docker compose up -d postgres

# Create virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Verify

```bash
# Health check
curl http://localhost:8000/health

# Swagger UI
open http://localhost:8000/docs
```

### Running Tests

```bash
cd backend
pip install -r requirements-dev.txt
pytest tests/ -v
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/documents/upload` | Upload a document |
| GET | `/api/v1/documents` | List documents (paginated) |
| GET | `/api/v1/documents/{id}` | Get document details |
| DELETE | `/api/v1/documents/{id}` | Delete a document |

## Project Structure

```
enterprise-ai-platform/
├── backend/
│   ├── app/
│   │   ├── api/          # Route handlers
│   │   ├── core/         # Config, logging
│   │   ├── db/           # Database engine + migrations
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   └── services/     # Business logic (Milestone 2+)
│   └── tests/
├── frontend/             # React UI (Milestone 5)
├── data/                 # Uploads + vector store
├── docs/                 # Architecture docs
└── docker-compose.yml
```

## Roadmap

- [x] **Milestone 1** — FastAPI + PostgreSQL + Document Upload
- [ ] **Milestone 2** — Document Processing → Embeddings → FAISS → Semantic Search
- [ ] **Milestone 3** — LLM → RAG → Citations → LangChain
- [ ] **Milestone 4** — Summarization → Extraction → Agents → Function Calling
- [ ] **Milestone 5** — React UI → Auth → Evaluation → Docker → CI/CD

## License

Private — All rights reserved.
