# Knowva AI

Knowva AI is a company knowledge chatbot backend built with FastAPI and retrieval-augmented generation (RAG). It indexes company documents in ChromaDB, retrieves relevant passages, and uses an OpenAI model to answer with source citations.

## Current features

- Upload PDF, DOCX, TXT, and Markdown documents
- Extract and chunk document text
- Generate OpenAI embeddings and persist them in ChromaDB
- Ask questions grounded in uploaded content
- Return document citations and excerpts
- List and delete indexed documents
- Interactive OpenAPI documentation

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

Add your OpenAI API key to `.env`, then start the API:

```bash
uvicorn app.main:app --reload
```

Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) to test the API in your browser.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/api/health` | Check API health |
| `POST` | `/api/documents` | Upload and index a document |
| `GET` | `/api/documents` | List indexed documents |
| `DELETE` | `/api/documents/{document_id}` | Delete a document |
| `POST` | `/api/query` | Ask the knowledge base a question |

Example query body:

```json
{
  "question": "What is the company's remote-work policy?"
}
```

## Run tests

```bash
pytest
```

