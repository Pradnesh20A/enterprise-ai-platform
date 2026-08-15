"""Tests for document management endpoints."""

import io

from httpx import AsyncClient


# ---------------------------------------------------------------------------
# Upload
# ---------------------------------------------------------------------------
class TestUploadDocument:
    """POST /api/v1/documents/upload"""

    async def test_upload_pdf_success(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Uploading a valid PDF should return 201 with document metadata."""
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("test_doc.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["original_filename"] == "test_doc.pdf"
        assert data["file_type"] == "pdf"
        assert data["file_size"] == len(sample_pdf_bytes)
        assert data["status"] == "uploaded"
        assert data["message"] == "Document uploaded successfully"
        assert "id" in data
        assert "created_at" in data

    async def test_upload_txt_success(
        self, client: AsyncClient, sample_txt_bytes: bytes
    ):
        """Uploading a valid TXT file should return 201."""
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("notes.txt", io.BytesIO(sample_txt_bytes), "text/plain")},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["file_type"] == "txt"

    async def test_upload_invalid_file_type(self, client: AsyncClient):
        """Uploading a disallowed file type should return 422."""
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("malware.exe", io.BytesIO(b"bad content"), "application/octet-stream")},
        )

        assert response.status_code == 422
        assert "not allowed" in response.json()["detail"].lower()

    async def test_upload_empty_file(self, client: AsyncClient):
        """Uploading an empty file should return 422."""
        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
        )

        assert response.status_code == 422
        assert "empty" in response.json()["detail"].lower()

    async def test_upload_oversized_file(self, client: AsyncClient, monkeypatch):
        """Uploading a file exceeding MAX_FILE_SIZE should return 413."""
        # Temporarily set a very small limit
        monkeypatch.setattr("app.core.config.settings.MAX_FILE_SIZE", 10)

        response = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("big.pdf", io.BytesIO(b"x" * 100), "application/pdf")},
        )

        assert response.status_code == 413
        assert "too large" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------
class TestListDocuments:
    """GET /api/v1/documents"""

    async def test_list_empty(self, client: AsyncClient):
        """Listing documents when none exist should return an empty list."""
        response = await client.get("/api/v1/documents")

        assert response.status_code == 200
        data = response.json()
        assert data["documents"] == []
        assert data["total"] == 0
        assert data["skip"] == 0
        assert data["limit"] == 20

    async def test_list_after_upload(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Documents should appear in the list after upload."""
        # Upload a document first
        await client.post(
            "/api/v1/documents/upload",
            files={"file": ("doc.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
        )

        response = await client.get("/api/v1/documents")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["documents"]) == 1
        assert data["documents"][0]["original_filename"] == "doc.pdf"

    async def test_list_pagination(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Pagination parameters should limit results correctly."""
        # Upload 3 documents
        for i in range(3):
            await client.post(
                "/api/v1/documents/upload",
                files={"file": (f"doc_{i}.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
            )

        response = await client.get("/api/v1/documents?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["documents"]) == 2
        assert data["limit"] == 2


# ---------------------------------------------------------------------------
# Get by ID
# ---------------------------------------------------------------------------
class TestGetDocument:
    """GET /api/v1/documents/{id}"""

    async def test_get_existing_document(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Getting an existing document should return its full details."""
        upload_resp = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("detail.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
        )
        doc_id = upload_resp.json()["id"]

        response = await client.get(f"/api/v1/documents/{doc_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == doc_id
        assert data["original_filename"] == "detail.pdf"

    async def test_get_nonexistent_document(self, client: AsyncClient):
        """Getting a non-existent document should return 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/documents/{fake_id}")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------
class TestDeleteDocument:
    """DELETE /api/v1/documents/{id}"""

    async def test_delete_existing_document(
        self, client: AsyncClient, sample_pdf_bytes: bytes
    ):
        """Deleting an existing document should return 204 and remove it."""
        upload_resp = await client.post(
            "/api/v1/documents/upload",
            files={"file": ("remove_me.pdf", io.BytesIO(sample_pdf_bytes), "application/pdf")},
        )
        doc_id = upload_resp.json()["id"]

        # Delete
        delete_resp = await client.delete(f"/api/v1/documents/{doc_id}")
        assert delete_resp.status_code == 204

        # Verify it's gone
        get_resp = await client.get(f"/api/v1/documents/{doc_id}")
        assert get_resp.status_code == 404

    async def test_delete_nonexistent_document(self, client: AsyncClient):
        """Deleting a non-existent document should return 404."""
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/api/v1/documents/{fake_id}")

        assert response.status_code == 404
