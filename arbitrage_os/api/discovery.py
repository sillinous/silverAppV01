import httpx
import logging
import os
import json
import tempfile
from typing import List, Dict, Any, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from arbitrage_os.db import models
from arbitrage_os.db.database import SessionLocal
from arbitrage_os.discovery.scraper import scrape_url
from arbitrage_os.discovery.ai_logic import analyze_description
from arbitrage_os.logistics.geocoding import cleanup_and_geocode
from arbitrage_os.verification.image_analyzer import analyze_image_for_hallmarks
from arbitrage_os.valuation.dashboard import calculate_roi
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Models / Schemas
class ItemBase(BaseModel):
    url: str
    description: Optional[str] = None
    analysis: Optional[str] = None
    status: str = "new"
    score: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    image_urls: Optional[str] = None # Storing JSON string of image URLs
    image_analysis_results: Optional[str] = None # Storing JSON string of Ximilar analysis results
    roi_analysis: Optional[str] = None # Storing JSON string of ROI analysis results

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int

    class Config:
        orm_mode = True

class MultiDiscoveryRequest(BaseModel):
    urls: List[str]


from arbitrage_os.tasks import process_discovery_task

@router.post("/", response_model=Item)
async def run_discovery(url: str, db: Session = Depends(get_db)):
    """
    Endpoint to initiate the discovery process for a given URL.
    This creates an item record and triggers a background task to do the heavy lifting.
    """
    # Create an initial item in the database to get an ID
    initial_item_data = {
        "url": url,
        "status": "pending",
    }
    db_item = models.Item(**initial_item_data)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    # Trigger the background task
    process_discovery_task.delay(db_item.id)

    return db_item

@router.post("/multiple/", response_model=List[Dict[str, Any]])
async def run_multiple_discoveries(request: MultiDiscoveryRequest, db: Session = Depends(get_db)):
    """
    Endpoint to run the discovery process for multiple URLs.
    """
    results = []
    for url in request.urls:
        try:
            item = await run_discovery(url, db)
            results.append({"url": url, "status": "success", "item_id": item.id})
        except HTTPException as e:
            results.append({"url": url, "status": "failed", "detail": e.detail})
        except Exception as e:
            results.append({"url": url, "status": "failed", "detail": str(e)})
    return results

@router.get("/items/", response_model=List[Item])
def get_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all items from the database.
    """
    items = db.query(models.Item).offset(skip).limit(limit).all()
    return items
