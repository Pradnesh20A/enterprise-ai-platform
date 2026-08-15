"""Document and DocumentChunk models."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class DocumentStatus(str, enum.Enum):
    """Processing status of an uploaded document."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class Document(Base):
    """An uploaded document with metadata and processing status."""

    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Stored filename (UUID-based)"
    )
    original_filename: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="User's original filename"
    )
    file_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="File extension: pdf, docx, txt, jpg, png"
    )
    file_size: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="File size in bytes"
    )
    file_path: Mapped[str] = mapped_column(
        String(500), nullable=False, comment="Path to stored file on disk"
    )
    status: Mapped[str] = mapped_column(
        String(20), server_default=DocumentStatus.UPLOADED.value
    )
    page_count: Mapped[int | None] = mapped_column(Integer)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSON, comment="Flexible document metadata as JSON"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="documents"
    )

    def __repr__(self) -> str:
        return f"<Document {self.original_filename}>"


class DocumentChunk(Base):
    """A chunk of text extracted from a document for embedding and retrieval."""

    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer, nullable=False, comment="Position of this chunk within the document"
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    page_number: Mapped[int | None] = mapped_column(Integer)
    section: Mapped[str | None] = mapped_column(String(255))
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSON)
    embedding_id: Mapped[str | None] = mapped_column(
        String(255), comment="Reference ID into the vector store"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    document: Mapped["Document"] = relationship(back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk doc={self.document_id} idx={self.chunk_index}>"
