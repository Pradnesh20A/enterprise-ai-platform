"""Shared Pydantic schemas used across multiple endpoints."""

from datetime import datetime

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Response schema for the health check endpoint."""

    status: str
    version: str
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str
    status_code: int
