from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone
from backend.core.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source_domain = Column(String(255), index=True)
    title = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    published_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    scraped_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    author = Column(String(255), nullable=True)
    credibility_score = Column(Float, nullable=True)
    
class Claim(Base):
    __tablename__ = "claims"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    article_id = Column(String(36), ForeignKey("articles.id"))
    claim_text = Column(Text, nullable=False)
    verdict = Column(String(50), nullable=True) # TRUE, FALSE, MIXED, UNVERIFIED
    analysis_report = Column(JSON, nullable=True) # Detailed component scores
    confidence = Column(Float, nullable=True)

class MultimodalEvidence(Base):
    __tablename__ = "multimodal_evidence"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    claim_id = Column(String(36), ForeignKey("claims.id"))
    media_url = Column(Text, nullable=True)
    media_type = Column(String(50)) # image, video, audio
    manipulation_probability = Column(Float) # Deepfake score
    ai_generated_probability = Column(Float)
    analysis_metadata = Column(JSON) # e.g. CLIP/BLIP visual insights
