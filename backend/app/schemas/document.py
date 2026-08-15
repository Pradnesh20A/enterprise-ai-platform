"""Pydantic schemas for document endpoints."""

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    """Response schema for a single document."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    page_count: int | None = None
    created_at: datetime
    updated_at: datetime


class DocumentListResponse(BaseModel):
    """Paginated list of documents."""

    documents: list[DocumentResponse]
    total: int
    skip: int
    limit: int


class DocumentUploadResponse(BaseModel):
    """Response after a successful document upload."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    status: str
    created_at: datetime
    message: str = "Document uploaded successfully"
