import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.document import Document, DocumentChunk
from app.schemas.search import SearchRequest, SearchResponse, SearchResultChunk
from app.services.embeddings import generate_embedding
from app.services.vector_store import search_vectors

router = APIRouter(prefix="/search", tags=["Search"])

@router.post("", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    db: AsyncSession = Depends(get_db),
) -> SearchResponse:
    """Perform a semantic search across all processed document chunks."""
    
    # 1. Embed the query
    query_embedding = generate_embedding(request.query)
    
    # 2. Search FAISS for top K matches
    faiss_results = search_vectors(query_embedding, k=request.limit)
    
    if not faiss_results:
        return SearchResponse(query=request.query, results=[], total_found=0)
        
    # 3. Retrieve chunk and document data from PostgreSQL
    search_results: List[SearchResultChunk] = []
    
    for chunk_id_str, score in faiss_results:
        try:
            chunk_id = uuid.UUID(chunk_id_str)
        except ValueError:
            continue
            
        # We need the chunk and its associated document
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.id == chunk_id)
            .options(selectinload(DocumentChunk.document))
        )
        result = await db.execute(stmt)
        chunk = result.scalar_one_or_none()
        
        if chunk and chunk.document:
            search_results.append(
                SearchResultChunk(
                    chunk_id=str(chunk.id),
                    content=chunk.content,
                    similarity_score=score,
                    document=chunk.document
                )
            )
            
    # Sort results by score descending (highest similarity first)
    search_results.sort(key=lambda x: x.similarity_score, reverse=True)
    
    return SearchResponse(
        query=request.query,
        results=search_results,
        total_found=len(search_results)
    )
