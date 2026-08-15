import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.document import DocumentChunk
from app.schemas.qa import QARequest, QAResponse, Citation
from app.services.embeddings import generate_embedding
from app.services.vector_store import search_vectors
from app.services.llm import llm_service

router = APIRouter(prefix="/qa", tags=["QA"])

@router.post("/ask", response_model=QAResponse)
async def ask_question(
    request: QARequest,
    db: AsyncSession = Depends(get_db),
) -> QAResponse:
    """Ask a question and get an answer based on uploaded documents."""
    
    # 1. Embed the question
    query_embedding = generate_embedding(request.question)
    
    # 2. Search FAISS for top K matches
    faiss_results = search_vectors(query_embedding, k=request.top_k)
    
    if not faiss_results:
        return QAResponse(
            answer="I don't have enough context in the uploaded documents to answer that question.",
            citations=[]
        )
        
    # 3. Retrieve chunk and document data from PostgreSQL
    citations = []
    context_chunks = []
    
    for chunk_id_str, _ in faiss_results:
        try:
            chunk_id = uuid.UUID(chunk_id_str)
        except ValueError:
            continue
            
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.id == chunk_id)
            .options(selectinload(DocumentChunk.document))
        )
        result = await db.execute(stmt)
        chunk = result.scalar_one_or_none()
        
        if chunk and chunk.document:
            context_chunks.append({
                "snippet": chunk.content
            })
            citations.append(
                Citation(
                    document_id=chunk.document.id,
                    filename=chunk.document.filename,
                    snippet=chunk.content[:200] + "..." # Snippet preview
                )
            )
            
    if not context_chunks:
         return QAResponse(
            answer="I couldn't retrieve the specific document contents to answer that question.",
            citations=[]
        )
        
    # 4. Generate answer using Gemini
    try:
        answer = llm_service.generate_rag_answer(request.question, context_chunks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
    return QAResponse(
        answer=answer,
        citations=citations
    )
