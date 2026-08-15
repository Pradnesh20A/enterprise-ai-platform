"""Document management endpoints: upload, list, get, delete."""

import uuid
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.database import get_db
from app.models.document import Document, DocumentStatus
from app.schemas.document import (
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
)
from app.services.document_processor import delete_document_chunks, process_document

router = APIRouter(prefix="/documents", tags=["Documents"])
logger = get_logger(__name__)


def _validate_file_type(file: UploadFile) -> str:
    """Validate the uploaded file has an allowed extension.

    Returns the lowercase extension string.
    Raises HTTPException 422 if the file type is not allowed.
    """
    if not file.filename:
        raise HTTPException(status_code=422, detail="Filename is required")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in settings.ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(settings.ALLOWED_EXTENSIONS))
        raise HTTPException(
            status_code=422,
            detail=f"File type '.{ext}' is not allowed. Allowed types: {allowed}",
        )
    return ext


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Document file to upload"),
    db: AsyncSession = Depends(get_db),
) -> DocumentUploadResponse:
    """Upload a document for processing.

    Accepts PDF, DOCX, TXT, JPG, and PNG files up to 50MB.
    The file is stored on disk and a database record is created
    with status 'uploaded'.
    """
    # Validate file type
    ext = _validate_file_type(file)

    # Read file content and validate size
    content = await file.read()
    file_size = len(content)

    if file_size == 0:
        raise HTTPException(status_code=422, detail="Uploaded file is empty")

    if file_size > settings.MAX_FILE_SIZE:
        max_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"File too large ({file_size:,} bytes). Maximum allowed: {max_mb}MB",
        )

    # Generate unique filename and save to disk
    file_id = uuid.uuid4()
    stored_filename = f"{file_id}.{ext}"
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / stored_filename

    file_path.write_bytes(content)

    logger.info(
        "document_uploaded",
        filename=file.filename,
        file_type=ext,
        file_size=file_size,
        document_id=str(file_id),
    )

    # Create database record
    document = Document(
        id=file_id,
        filename=stored_filename,
        original_filename=file.filename,
        file_type=ext,
        file_size=file_size,
        file_path=str(file_path),
        status=DocumentStatus.UPLOADED.value,
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)

    # Enqueue background processing (parse -> chunk -> embed -> FAISS)
    background_tasks.add_task(
        process_document,
        db=db,
        document_id=file_id,
        file_content=content,
        file_type=ext
    )

    return DocumentUploadResponse(
        id=document.id,
        filename=document.filename,
        original_filename=document.original_filename,
        file_type=document.file_type,
        file_size=document.file_size,
        status=document.status,
        created_at=document.created_at,
        message="Document uploaded successfully",
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    """List all uploaded documents with pagination.

    Returns documents ordered by upload date (newest first).
    """
    # Total count
    count_result = await db.execute(select(func.count(Document.id)))
    total = count_result.scalar_one()

    # Paginated query
    result = await db.execute(
        select(Document).order_by(Document.created_at.desc()).offset(skip).limit(limit)
    )
    documents = result.scalars().all()

    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    """Get details of a specific document by ID."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a document and remove its file from disk.

    Also cascades to delete any associated chunks.
    """
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Clean up vector store and chunk DB records
    await delete_document_chunks(db, document.id)

    # Remove file from disk
    file_path = Path(document.file_path)
    if file_path.exists():
        file_path.unlink()

    # Delete database record (cascades to chunks)
    await db.delete(document)

    logger.info("document_deleted", document_id=str(document_id))
