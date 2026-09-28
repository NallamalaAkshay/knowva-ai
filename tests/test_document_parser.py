from app.document_parser import chunk_text, extract_text


def test_extracts_utf8_text() -> None:
    assert extract_text("policy.txt", b"Remote work policy") == "Remote work policy"


def test_chunks_text_with_overlap() -> None:
    text = "one two three four five six seven eight nine ten"
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    assert len(chunks) > 1
    assert "one two" in chunks[0]
    assert "ten" in chunks[-1]

