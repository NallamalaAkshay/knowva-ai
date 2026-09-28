from fastapi.testclient import TestClient

from app.main import app, get_rag_service
from app.schemas import DocumentSummary, QueryResponse


class FakeRagService:
    def __init__(self) -> None:
        self.documents: dict[str, tuple[str, int]] = {}

    def add_document(self, filename: str, chunks: list[str]) -> str:
        self.documents["doc-1"] = (filename, len(chunks))
        return "doc-1"

    def list_documents(self) -> list[DocumentSummary]:
        return [
            DocumentSummary(document_id=key, filename=value[0], chunks=value[1])
            for key, value in self.documents.items()
        ]

    def delete_document(self, document_id: str) -> bool:
        return self.documents.pop(document_id, None) is not None

    def answer(self, question: str) -> QueryResponse:
        return QueryResponse(answer=f"Answer to: {question}", citations=[])


fake_rag = FakeRagService()
app.dependency_overrides[get_rag_service] = lambda: fake_rag
client = TestClient(app)


def test_health() -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_upload_and_list_document() -> None:
    response = client.post(
        "/api/documents",
        files={"file": ("handbook.txt", b"Employees receive paid time off.", "text/plain")},
    )
    assert response.status_code == 201
    assert response.json()["document_id"] == "doc-1"

    documents = client.get("/api/documents")
    assert documents.status_code == 200
    assert documents.json()[0]["filename"] == "handbook.txt"


def test_rejects_unsupported_file() -> None:
    response = client.post(
        "/api/documents",
        files={"file": ("image.png", b"not an image", "image/png")},
    )
    assert response.status_code == 400


def test_query() -> None:
    response = client.post("/api/query", json={"question": "What is the PTO policy?"})
    assert response.status_code == 200
    assert "PTO policy" in response.json()["answer"]

