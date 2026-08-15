import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.database import get_db
from app.models.document import DocumentChunk
from app.models.conversation import Conversation, Message
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.qa import QARequest, QAResponse, Citation
from app.services.embeddings import generate_embedding
from app.services.vector_store import search_vectors
from app.services.llm import llm_service

router = APIRouter(prefix="/qa", tags=["Q&A"])

@router.post("/ask", response_model=QAResponse)
async def ask_question(
    request: QARequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QAResponse:
    # 1. Embed the question
    query_embedding = generate_embedding(request.question)
    
    # 2. Search FAISS for top K matches (fetch more to account for cross-tenant filtering)
    faiss_results = search_vectors(query_embedding, k=request.top_k * 5)
    
    if not faiss_results:
        return QAResponse(
            answer="I don't have enough context in the uploaded documents to answer that question.",
            citations=[]
        )
        
    # 3. Retrieve chunk and document data from PostgreSQL, ensuring they belong to current_user
    citations = []
    context_chunks = []
    
    for chunk_id_str, _ in faiss_results:
        if len(context_chunks) >= request.top_k:
            break
            
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
        
        if chunk and chunk.document and chunk.document.uploaded_by == current_user.id:
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
        
    # 4. Handle Conversation DB state
    conversation = None
    chat_history = []
    
    if request.conversation_id:
        # Fetch existing conversation
        stmt = (
            select(Conversation)
            .where(
                Conversation.id == request.conversation_id,
                Conversation.user_id == current_user.id
            )
            .options(selectinload(Conversation.messages))
        )
        result = await db.execute(stmt)
        conversation = result.scalar_one_or_none()
        
        if conversation:
            # Order messages chronologically
            sorted_messages = sorted(conversation.messages, key=lambda m: m.created_at)
            chat_history = [{"role": m.role, "content": m.content} for m in sorted_messages]
            
    if not conversation:
        # Create new conversation
        title = request.question[:50] + "..." if len(request.question) > 50 else request.question
        conversation = Conversation(
            user_id=current_user.id,
            title=title
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        
    # Save user message
    user_message = Message(
        conversation_id=conversation.id,
        role="user",
        content=request.question
    )
    db.add(user_message)
    await db.commit()

    # 5. Generate answer using Gemini
    try:
        answer = await llm_service.generate_rag_answer(
            question=request.question, 
            context_chunks=context_chunks,
            history=chat_history,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            db=db,
            user_id=current_user.id
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
    # Save assistant message
    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
        sources=[c.model_dump(mode="json") for c in citations]
    )
    db.add(assistant_message)
    
    # Update conversation timestamp
    conversation.updated_at = func.now()
    await db.commit()
        
    return QAResponse(
        answer=answer,
        citations=citations,
        conversation_id=conversation.id
    )
