<div align="center">

# Knowva AI

### Database-aware company knowledge and careers assistant

Knowva AI combines structured company data with retrieval-augmented generation (RAG) to answer natural-language questions about companies, offices, jobs, and uploaded documents.

![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-TypeScript-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

</div>

![Knowva AI dashboard](docs/images/knowva-ai-dashboard.png)

## Overview

Knowva AI is a full-stack AI application for managing company information and querying it conversationally. It stores structured company, office, and job records in PostgreSQL, indexes uploaded documents in ChromaDB, and uses OpenAI models to generate grounded answers.

The chat endpoint follows a hybrid retrieval strategy:

1. Search current company, office, and job records in PostgreSQL.
2. If the structured database cannot answer the question, retrieve relevant document chunks from ChromaDB.
3. Generate a concise answer from the retrieved context.
4. Return supporting document citations when the answer comes from the knowledge base.

## Features

- Natural-language questions about company information and job openings
- Company, office, and job CRUD APIs
- Job filtering by location, title, department, work model, experience, and status
- PDF, DOCX, TXT, and Markdown document uploads
- Paragraph-aware text extraction and chunking
- OpenAI embeddings for semantic retrieval
- Persistent document vectors and metadata in ChromaDB
- Database-first chat with RAG fallback
- Source-grounded answers with compact citations
- React and TypeScript chat interface
- Interactive OpenAPI documentation through Swagger UI
- PostgreSQL with pgvector running through Docker Compose

## Application Preview

### Natural-language job discovery

Users can ask questions such as *“Which jobs are available in Albany, New York?”* and receive matching positions with job codes, work models, experience ranges, salary ranges, and application links.

![Natural-language job search](docs/images/job-search-results.png)

### Interactive API documentation

FastAPI automatically exposes searchable Swagger documentation for Companies, Offices, Jobs, System, Knowledge Base, and Chat operations.

![Knowva AI Swagger API overview](docs/images/swagger-api-overview.png)

### Job management API

The Jobs API supports creating, listing, retrieving, updating, and deleting job records.

![Knowva AI Jobs API](docs/images/jobs-api.png)

## Architecture

```mermaid
flowchart TD
    UI[React + TypeScript UI] --> API[FastAPI REST API]
    API --> DB[(PostgreSQL + pgvector)]
    API --> CHAT[Database-aware Chat Service]
    CHAT --> DB
    CHAT --> RAG[RAG Service]
    RAG --> OPENAI[OpenAI API]
    RAG --> CHROMA[(ChromaDB)]
    DOCS[PDF / DOCX / TXT / MD] --> PARSER[Parser + Chunker]
    PARSER --> RAG
```

## Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, TypeScript, Vite, Lucide React |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| Structured data | PostgreSQL, SQLAlchemy, Psycopg, pgvector |
| RAG storage | ChromaDB Persistent Client |
| AI | OpenAI chat completions and embeddings |
| Document processing | pypdf, python-docx |
| Infrastructure | Docker Compose |
| Testing | pytest, HTTPX |

## Project Structure

```text
knowva-ai/
├── app/
│   ├── main.py                   # FastAPI application and API composition
│   ├── config.py                 # Environment-based settings
│   ├── database.py               # SQLAlchemy engine and sessions
│   ├── models.py                 # Company, Office, and Job models
│   ├── company_routes.py         # Company CRUD endpoints
│   ├── company_schemas.py        # Company request/response schemas
│   ├── office_routes.py          # Office CRUD endpoints
│   ├── office_schemas.py         # Office request/response schemas
│   ├── job_routes.py             # Job CRUD and filtering endpoints
│   ├── job_schemas.py            # Job request/response schemas
│   ├── database_chat_service.py  # Structured database question answering
│   ├── document_parser.py        # File extraction and chunking
│   ├── rag_service.py            # Embedding, retrieval, and answer logic
│   └── schemas.py                # Knowledge-base and chat schemas
├── frontend/
│   ├── src/App.tsx               # Main chat interface
│   ├── src/api.ts                # Typed API client
│   └── src/styles.css            # Application styling
├── docs/images/                  # README screenshots
├── tests/                        # Backend tests
├── docker-compose.yml            # PostgreSQL + pgvector service
├── seed_jobs.py                  # Sample job data
├── pyproject.toml                # Python project configuration
├── .env.example                  # Environment-variable template
└── README.md
```

## Prerequisites

Install the following before running the project:

- Python 3.11 or later
- Node.js 18 or later
- npm
- Docker Desktop
- An OpenAI API key for document indexing and AI-generated answers

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/NallamalaAkshay/knowva-ai.git
cd knowva-ai
```

### 2. Configure the backend

Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the backend and development dependencies:

```bash
pip install -e '.[dev]'
pip install sqlalchemy "psycopg[binary]" alembic pgvector
```

Create the local environment file:

```bash
cp .env.example .env
```

Add your own OpenAI key to `.env`:

```env
APP_NAME=Knowva AI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=postgresql+psycopg://knowva:knowva_local_password@localhost:5433/knowva
CHROMA_PATH=./data/chroma
MAX_UPLOAD_MB=10
CHUNK_SIZE=2500
CHUNK_OVERLAP=300
RETRIEVAL_COUNT=20
```

> Never commit `.env` or a real API key. Only `.env.example` should be tracked by Git.

### 3. Start PostgreSQL

Open Docker Desktop, then run:

```bash
docker compose up -d
docker compose ps
```

Enable the vector extension if it has not already been enabled:

```bash
docker exec -it knowva-postgres \
  psql -U knowva -d knowva \
  -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

The database is exposed on host port `5433` to avoid conflicts with an existing local PostgreSQL installation.

### 4. Start the FastAPI backend

```bash
uvicorn app.main:app --reload
```

Backend URLs:

- API root: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- OpenAPI schema: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

### 5. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173).

## API Endpoints

| Group | Method | Endpoint | Purpose |
|---|---|---|---|
| System | `GET` | `/api/health` | Check API health |
| Companies | `POST` | `/api/companies` | Create a company |
| Companies | `GET` | `/api/companies` | List and filter companies |
| Companies | `GET` | `/api/companies/{company_id}` | Retrieve a company |
| Companies | `PUT` | `/api/companies/{company_id}` | Update a company |
| Companies | `DELETE` | `/api/companies/{company_id}` | Delete a company |
| Offices | `POST` | `/api/offices` | Create an office |
| Offices | `GET` | `/api/offices` | List and filter offices |
| Offices | `GET` | `/api/offices/{office_id}` | Retrieve an office |
| Offices | `PUT` | `/api/offices/{office_id}` | Update an office |
| Offices | `DELETE` | `/api/offices/{office_id}` | Delete an office |
| Jobs | `POST` | `/api/jobs` | Create a job |
| Jobs | `GET` | `/api/jobs` | List, search, and filter jobs |
| Jobs | `GET` | `/api/jobs/{job_id}` | Retrieve a job |
| Jobs | `PUT` | `/api/jobs/{job_id}` | Update a job |
| Jobs | `DELETE` | `/api/jobs/{job_id}` | Delete a job |
| Knowledge Base | `POST` | `/api/documents` | Upload and index a document |
| Knowledge Base | `GET` | `/api/documents` | List indexed documents |
| Knowledge Base | `DELETE` | `/api/documents/{document_id}` | Delete an indexed document |
| Chat | `POST` | `/api/query` | Ask a database-aware or RAG question |

## Example Chat Request

```bash
curl -X POST http://127.0.0.1:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Which jobs are available in Albany, New York?"
  }'
```

Example response shape:

```json
{
  "answer": "The matching open positions are ...",
  "citations": []
}
```

Document-grounded responses include citations containing the source document, chunk number, and excerpt.

## Running Tests

With the virtual environment activated:

```bash
pytest
```

Build the frontend:

```bash
cd frontend
npm run build
```

## Stopping the Project

Stop the frontend and backend with `Ctrl+C`, then stop the database:

```bash
docker compose down
```

Do not add `-v` unless you intentionally want to delete the PostgreSQL volume and all stored database data.

## Security Notes

- Keep `.env`, API keys, database files, Chroma data, virtual environments, and `node_modules` out of Git.
- Rotate an API key immediately if it is committed or shared accidentally.
- The current project is a local-development MVP and does not include authentication or authorization for CRUD endpoints.
- Add authentication, rate limiting, stricter CORS settings, upload validation, and audit logging before production deployment.

## Current Limitations

- Chat and document indexing require a valid OpenAI API key and available API credits.
- The frontend currently displays model-generated Markdown as plain text.
- SQLAlchemy creates missing tables at startup; production deployments should use Alembic migrations.
- ChromaDB is configured as a local persistent vector store.
- Sample application URLs and company records are demonstration data.

## Future Improvements

- Authentication and role-based administration
- Company, office, and job management screens in the frontend
- Render Markdown answers with sanitized clickable links
- Hybrid keyword and vector retrieval
- Structured citations for database-derived answers
- Alembic database migrations
- Automated CI checks and deployment
- Production-ready logging, monitoring, and rate limiting

## Author

**Akshay Nallamala**

Built as a full-stack AI and data engineering project demonstrating RAG, semantic search, relational data modeling, REST API development, and modern React development.

