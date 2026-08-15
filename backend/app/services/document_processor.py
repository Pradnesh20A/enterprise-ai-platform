import logging
import uuid
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentChunk, DocumentStatus
from app.services.chunking import chunk_text
from app.services.embeddings import generate_embeddings
from app.services.parsers import parse_document
from app.services.vector_store import add_vectors, delete_vectors

logger = logging.getLogger(__name__)


async def process_document(
    db: AsyncSession, document_id: uuid.UUID, file_content: bytes, file_type: str
) -> None:
    """End-to-end pipeline to parse, chunk, embed, and store a document.
    
    This is intended to be run as a background task.
    """
    logger.info(f"Starting processing for document {document_id}")
    
    # 1. Update status to processing
    document = await db.get(Document, document_id)
    if not document:
        logger.error(f"Document {document_id} not found.")
        return
        
    document.status = DocumentStatus.PROCESSING.value
    await db.commit()
    
    try:
        # 2. Parse text
        logger.info(f"Parsing {file_type} document {document_id}")
        text = await parse_document(file_content, file_type)
        
        if not text:
            raise ValueError(f"Failed to extract text from {file_type} file or unsupported format.")
            
        # 3. Chunk text
        logger.info(f"Chunking text for document {document_id}")
        chunks_text = chunk_text(text)
        logger.info(f"Created {len(chunks_text)} chunks for document {document_id}")
        
        if not chunks_text:
            raise ValueError("No text chunks generated.")
            
        # 4. Generate Embeddings
        logger.info(f"Generating embeddings for {len(chunks_text)} chunks")
        embeddings = generate_embeddings(chunks_text)
        
        # 5. Save to DB and Vector Store
        chunk_ids = []
        db_chunks = []
        
        for i, (chunk_content, embedding) in enumerate(zip(chunks_text, embeddings)):
            chunk_id = uuid.uuid4()
            chunk_ids.append(str(chunk_id))
            
            db_chunk = DocumentChunk(
                id=chunk_id,
                document_id=document_id,
                chunk_index=i,
                content=chunk_content,
                # For now, we don't have page numbers from PyMuPDF in this simple implementation,
                # but we could add them by yielding page-by-page from parse_document.
            )
            db_chunks.append(db_chunk)
            
        # Add to PostgreSQL
        db.add_all(db_chunks)
        
        # Add to FAISS
        add_vectors(embeddings, chunk_ids)
        
        # 6. Update final status
        document.status = DocumentStatus.PROCESSED.value
        await db.commit()
        logger.info(f"Successfully processed document {document_id}")
        
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}")
        await db.rollback()
        
        # Reload document to update status to failed
        document = await db.get(Document, document_id)
        if document:
            document.status = DocumentStatus.FAILED.value
            await db.commit()


async def delete_document_chunks(db: AsyncSession, document_id: uuid.UUID) -> None:
    """Deletes all chunks associated with a document from the DB and Vector Store."""
    # First get all chunks to find their IDs for FAISS deletion
    from sqlalchemy import select
    result = await db.execute(select(DocumentChunk).where(DocumentChunk.document_id == document_id))
    chunks = result.scalars().all()
    
    if chunks:
        chunk_ids = [str(c.id) for c in chunks]
        
        # Delete from FAISS
        delete_vectors(chunk_ids)
        
        # Delete from DB
        # SQLAlchemy cascade delete on Document will handle deleting DocumentChunk records
        # when the Document is deleted, but if we call this directly we need to delete them.
        for chunk in chunks:
            await db.delete(chunk)
            
        await db.commit()
