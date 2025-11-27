"""
Pydantic models for API requests and responses.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class LoginRequest(BaseModel):
    """Login request model."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration in seconds")


class LogSearchRequest(BaseModel):
    """Log search request model."""
    query: Optional[str] = Field(None, description="Full-text search query")
    severity: Optional[List[str]] = Field(None, description="Severity levels to filter")
    facility: Optional[List[str]] = Field(None, description="Facilities to filter")
    hostname: Optional[str] = Field(None, description="Hostname to filter")
    start_time: Optional[datetime] = Field(None, description="Start time for time range")
    end_time: Optional[datetime] = Field(None, description="End time for time range")
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(100, ge=1, le=1000, description="Number of results per page")
    sort_by: str = Field("received_at", description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order (asc or desc)")


class LogResponse(BaseModel):
    """Log document response model."""
    timestamp: Optional[str] = None
    received_at: str
    processed_at: Optional[str] = None
    source_ip: str
    hostname: str
    facility: int
    facility_name: str
    severity: int
    severity_name: str
    severity_category: str
    message: str
    protocol: str
    format: str
    tags: List[str] = []
    has_threat_indicators: bool = False
    threat_score: int = 0


class LogSearchResponse(BaseModel):
    """Log search response model."""
    total: int = Field(..., description="Total number of matching logs")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of results per page")
    total_pages: int = Field(..., description="Total number of pages")
    logs: List[dict] = Field(..., description="Log entries")


class StatisticsResponse(BaseModel):
    """Statistics response model."""
    total_logs: int
    by_severity: dict
    by_facility: dict
    top_hosts: List[dict]
    timeline: List[dict]
    threat_logs_count: int


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    dependencies: dict = Field(..., description="Dependency status")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Additional error details")
