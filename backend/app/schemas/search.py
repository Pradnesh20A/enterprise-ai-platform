from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.document import DocumentResponse


class SearchRequest(BaseModel):
    """Request schema for semantic search."""
    
    query: str = Field(..., min_length=1, description="The search query.")
    limit: int = Field(5, ge=1, le=20, description="Maximum number of results to return.")
    # We could add filters here later (e.g., document_id, date range)

class SearchResultChunk(BaseModel):
    """Schema for a matched document chunk in search results."""
    
    chunk_id: str
    content: str
    similarity_score: float
    # Include the document this chunk belongs to
    document: DocumentResponse

class SearchResponse(BaseModel):
    """Response schema for semantic search."""
    
    query: str
    results: List[SearchResultChunk]
    total_found: int
