from sqlalchemy import Column, Integer, String, Text, DateTime, func, Boolean
from .database import Base

class ScrapingSource(Base):
    __tablename__ = "scraping_sources"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    last_scraped = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
