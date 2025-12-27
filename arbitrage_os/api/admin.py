import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from arbitrage_os.api.discovery import run_discovery
from arbitrage_os.db.database import SessionLocal
from arbitrage_os.db.scraping_source import ScrapingSource as ScrapingSourceModel

logger = logging.getLogger(__name__)
router = APIRouter()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class ScrapingSourceCreate(BaseModel):
    url: str
    name: Optional[str] = None
    is_active: bool = True

@router.post("/add_scraping_source/", response_model=ScrapingSourceCreate)
def add_scraping_source(source: ScrapingSourceCreate, db: Session = Depends(get_db)):
    """
    Endpoint to add a new scraping source to the database.
    """
    db_source = ScrapingSourceModel(**source.dict())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

@router.post("/run_scheduled_scrape/")
async def run_scheduled_scrape(db: Session = Depends(get_db)):
    """
    Endpoint to run a scheduled scrape for all active sources.
    """
    sources = db.query(ScrapingSourceModel).filter(ScrapingSourceModel.is_active == True).all()
    
    all_results = []
    for source in sources:
        try:
            # For now, we'll just call run_discovery for each source URL
            # In a real scenario, this might involve more complex scraping logic
            # that yields multiple URLs from a single source.
            item = await run_discovery(source.url, db)
            source.last_scraped = datetime.now()
            db.add(source)
            db.commit()
            db.refresh(source)
            all_results.append({"source_url": source.url, "status": "success", "item_id": item.id})
        except HTTPException as e:
            all_results.append({"source_url": source.url, "status": "failed", "detail": e.detail})
        except Exception as e:
            all_results.append({"source_url": source.url, "status": "failed", "detail": str(e)})
            logger.error(f"Error during scheduled scrape for source {source.url}: {e}")
            
    return {"message": "Scheduled scrape completed", "results": all_results}
