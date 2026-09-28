from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import models so SQLAlchemy registers all database tables.
from app.models import Company, Job, Office  # noqa: F401

from app.company_routes import router as company_router
from app.config import Settings, get_settings
from app.database import Base, engine, get_database_session
from app.database_chat_service import answer_database_question
from app.document_parser import chunk_text, extract_text
from app.job_routes import router as job_router
from app.office_routes import router as office_router
from app.rag_service import RagService
from app.schemas import (
    DocumentResponse,
    DocumentSummary,
    HealthResponse,
    QueryRequest,
    QueryResponse,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables that do not already exist.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Knowva AI API",
    description=(
        "Store company, office, and job information; upload company "
        "documents; and ask database-aware, source-grounded questions."
    ),
    version="0.5.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Activate database API endpoints.
app.include_router(company_router)
app.include_router(office_router)
app.include_router(job_router)


# Create one shared RAG service and ChromaDB client.
rag_service = RagService(
    get_settings()
)


def get_rag_service() -> RagService:
    return rag_service


@app.get(
    "/",
    include_in_schema=False,
)
def root() -> dict[str, str]:
    return {
        "message": "Knowva AI API",
        "docs": "/docs",
    }


@app.get(
    "/api/health",
    response_model=HealthResponse,
    tags=["System"],
)
def health(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    return HealthResponse(
        status="ok",
        app=settings.app_name,
    )


@app.post(
    "/api/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Knowledge Base"],
)
async def upload_document(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings),
    rag: RagService = Depends(get_rag_service),
) -> DocumentResponse:
    filename = Path(
        file.filename or ""
    ).name

    if not filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A filename is required",
        )

    maximum_bytes = (
        settings.max_upload_mb
        * 1024
        * 1024
    )

    content = await file.read(
        maximum_bytes + 1
    )

    if len(content) > maximum_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File is too large",
        )

    try:
        text = extract_text(
            filename,
            content,
        )

        chunks = chunk_text(
            text,
            settings.chunk_size,
            settings.chunk_overlap,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "The document contains no readable text"
            ),
        )

    try:
        document_id = rag.add_document(
            filename,
            chunks,
        )
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    return DocumentResponse(
        document_id=document_id,
        filename=filename,
        chunks=len(chunks),
        message="Document indexed successfully",
    )


@app.get(
    "/api/documents",
    response_model=list[DocumentSummary],
    tags=["Knowledge Base"],
)
def list_documents(
    rag: RagService = Depends(get_rag_service),
) -> list[DocumentSummary]:
    return rag.list_documents()


@app.delete(
    "/api/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Knowledge Base"],
)
def delete_document(
    document_id: str,
    rag: RagService = Depends(get_rag_service),
) -> None:
    deleted = rag.delete_document(
        document_id
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )


@app.post(
    "/api/query",
    response_model=QueryResponse,
    tags=["Chat"],
)
def query(
    request: QueryRequest,
    database: Session = Depends(get_database_session),
    rag: RagService = Depends(get_rag_service),
) -> QueryResponse:
    try:
        # First, check current company, office, and job records
        # stored in PostgreSQL.
        database_answer = answer_database_question(
            database,
            request.question,
        )

        if database_answer is not None:
            return QueryResponse(
                answer=database_answer,
                citations=[],
            )

        # If PostgreSQL cannot answer, use uploaded documents.
        return rag.answer(
            request.question
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc