from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

class QARequest(BaseModel):
    question: str
    top_k: int = 5

class Citation(BaseModel):
    document_id: UUID
    filename: str
    snippet: str

class QAResponse(BaseModel):
    answer: str
    citations: List[Citation]
