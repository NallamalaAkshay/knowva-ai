from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    app: str


class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    chunks: int
    message: str


class DocumentSummary(BaseModel):
    document_id: str
    filename: str
    chunks: int


class QueryRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)


class Citation(BaseModel):
    document_id: str
    filename: str
    chunk: int
    excerpt: str


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]

