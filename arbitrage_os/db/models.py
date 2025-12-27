from sqlalchemy import Column, Integer, String, Text, DateTime, func, Float

from .database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    description = Column(Text, nullable=True)
    analysis = Column(Text, nullable=True)  # For storing AI reasoning
    status = Column(String, default="new")
    
    # Structured data fields
    score = Column(Integer, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    image_urls = Column(Text, nullable=True) # Storing list of URLs as a JSON string
    image_analysis_results = Column(Text, nullable=True) # Storing JSON string of Ximilar analysis results
    roi_analysis = Column(Text, nullable=True) # Storing JSON string of ROI analysis results

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
