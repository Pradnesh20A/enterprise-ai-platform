from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel

from app.api.deps import get_current_admin_user
from app.db.database import get_db
from app.models.user import User
from app.models.document import Document
from app.models.conversation import Conversation
from app.models.document import DocumentChunk

router = APIRouter(prefix="/admin", tags=["Admin"])

class AdminStatsResponse(BaseModel):
    total_users: int
    total_documents: int
    total_chunks: int
    total_conversations: int

class AdminUserItem(BaseModel):
    id: UUID
    email: str
    role: str
    created_at: datetime
    document_count: int

@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    users_result = await db.execute(select(func.count()).select_from(User))
    docs_result = await db.execute(select(func.count()).select_from(Document))
    chunks_result = await db.execute(select(func.count()).select_from(DocumentChunk))
    convs_result = await db.execute(select(func.count()).select_from(Conversation))
    
    return AdminStatsResponse(
        total_users=users_result.scalar_one(),
        total_documents=docs_result.scalar_one(),
        total_chunks=chunks_result.scalar_one(),
        total_conversations=convs_result.scalar_one()
    )

@router.get("/users", response_model=List[AdminUserItem])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    stmt = (
        select(User, func.count(Document.id).label('document_count'))
        .outerjoin(Document, User.id == Document.uploaded_by)
        .group_by(User.id)
        .order_by(User.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()
    
    users = []
    for user, doc_count in rows:
        users.append(AdminUserItem(
            id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
            document_count=doc_count
        ))
    return users
