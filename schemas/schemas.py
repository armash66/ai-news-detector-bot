"""Pydantic schemas for Event API requests and responses."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ── Event Schemas ────────────────────────────────────────────────

class EventBase(BaseModel):
    title: str
    summary: Optional[str] = None
    category: str = "GENERAL"
    status: str = "EMERGING"


class EventResponse(EventBase):
    id: str
    significance_score: float = 0.0
    trust_score: float = 0.5
    article_count: int = 0
    source_count: int = 0
    first_seen_at: datetime
    last_updated_at: datetime
    peak_at: Optional[datetime] = None
    primary_location: Optional[Dict[str, Any]] = None
    primary_entities: Optional[List[Dict[str, str]]] = None
    sentiment_distribution: Optional[Dict[str, float]] = None
    parent_event_id: Optional[str] = None

    class Config:
        from_attributes = True


class EventDetail(EventResponse):
    """Extended event with related articles and timeline."""
    articles: List["ArticleResponse"] = []
    timeline: List["TimelineEntryResponse"] = []
    claims: List["ClaimResponse"] = []


class EventListResponse(BaseModel):
    data: List[EventResponse]
    meta: Dict[str, Any]


# ── Article Schemas ──────────────────────────────────────────────

class ArticleResponse(BaseModel):
    id: str
    source_domain: str = ""
    source_name: str = ""
    title: str
    summary: Optional[str] = None
    url: str = ""
    published_at: Optional[datetime] = None
    sentiment_score: Optional[float] = None
    credibility_score: Optional[float] = None
    language: str = "en"

    class Config:
        from_attributes = True


# ── Claim Schemas ────────────────────────────────────────────────

class ClaimResponse(BaseModel):
    id: str
    claim_text: str
    claim_type: str = "FACTUAL"
    verdict: str = "UNVERIFIED"
    confidence: Optional[float] = None
    supporting_sources: int = 0
    contradicting_sources: int = 0

    class Config:
        from_attributes = True


# ── Timeline Schemas ─────────────────────────────────────────────

class TimelineEntryResponse(BaseModel):
    id: str
    timestamp: datetime
    description: str
    entry_type: str = "UPDATE"
    significance: float = 0.5

    class Config:
        from_attributes = True


# ── Source Schemas ───────────────────────────────────────────────

class SourceResponse(BaseModel):
    id: str
    domain: str
    name: str
    source_type: str
    reliability_score: float
    bias_rating: str
    country: Optional[str] = None
    is_verified: bool = False

    class Config:
        from_attributes = True


# ── Search Schemas ───────────────────────────────────────────────

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    search_type: str = "keyword"  # keyword, semantic, hybrid
    filters: Optional[Dict[str, Any]] = None
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1, le=100)


class SearchResponse(BaseModel):
    data: List[EventResponse]
    meta: Dict[str, Any]


# ── Alert Schemas ────────────────────────────────────────────────

class AlertResponse(BaseModel):
    id: str
    event_id: Optional[str] = None
    alert_type: str
    severity: str
    title: str
    description: Optional[str] = None
    triggered_at: datetime
    acknowledged: bool = False

    class Config:
        from_attributes = True


# ── Trust Schemas ────────────────────────────────────────────────

class TrustExplanation(BaseModel):
    score: float
    breakdown: Dict[str, Dict[str, Any]]


class AnalyzeRequest(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None


class AnalyzeResponse(BaseModel):
    id: str
    status: str  # PENDING, PROCESSING, DONE
    result: Optional[Dict[str, Any]] = None


# Resolve forward references
EventDetail.model_rebuild()
