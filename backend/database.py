import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./intelligence.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ArticleModel(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), unique=True, index=True, nullable=True)
    title = Column(String(1024), nullable=True)
    author = Column(String(255), nullable=True)
    source = Column(String(255), index=True, nullable=True)
    published_date = Column(DateTime, nullable=True)
    text_content = Column(Text, nullable=False)
    image_url = Column(String(2048), nullable=True)
    
    # Analysis results JSON
    credibility_score = Column(Float, nullable=True)
    verdict = Column(String(50), nullable=True)
    claims = Column(JSON, nullable=True)
    evidence = Column(JSON, nullable=True)
    component_scores = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
