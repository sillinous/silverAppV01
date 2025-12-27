from celery import Celery
import logging
import os
import json
import tempfile
import httpx
from sqlalchemy.orm import Session
from arbitrage_os.db.database import SessionLocal
from arbitrage_os.db import models
from arbitrage_os.discovery.scraper import scrape_url
from arbitrage_os.discovery.ai_logic import analyze_description
from arbitrage_os.logistics.geocoding import cleanup_and_geocode
from arbitrage_os.verification.image_analyzer import analyze_image_for_hallmarks
from arbitrage_os.valuation.dashboard import calculate_roi

logger = logging.getLogger(__name__)

# Configure Celery
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="tasks.process_discovery")
def process_discovery_task(item_id: int):
    """
    Celery task to perform the heavy lifting of the discovery process.
    """
    db: Session = SessionLocal()
    try:
        item = db.query(models.Item).filter(models.Item.id == item_id).first()
        if not item:
            logger.error(f"Item with id {item_id} not found.")
            return

        # 1. Scrape URL
        item.status = "scraping"
        db.commit()
        scraped_data = scrape_url(item.url)
        description = scraped_data.get("text", "")
        image_urls = scraped_data.get("image_urls", [])
        item.description = description
        item.image_urls = json.dumps(image_urls) if image_urls else None
        if not description:
            item.status = "failed_scraping"
            db.commit()
            logger.error(f"Failed to scrape content from URL: {item.url}")
            return

        # 2. Analyze Description with AI
        item.status = "analyzing_text"
        db.commit()
        analysis_result = analyze_description(description)
        item.analysis = analysis_result.get("reasoning")
        item.score = analysis_result.get("score")
        raw_address = analysis_result.get("address")
        extracted_weight_grams = analysis_result.get("weight_grams")
        extracted_purity = analysis_result.get("purity")

        # 3. Geocode Address
        if raw_address and raw_address != "Not found":
            item.status = "geocoding"
            db.commit()
            geocoded_data = cleanup_and_geocode(raw_address)
            if geocoded_data and isinstance(geocoded_data, dict):
                item.latitude = geocoded_data.get("lat")
                item.longitude = geocoded_data.get("lng")
            else:
                logger.warning(f"Geocoding failed for address: {raw_address}")

        # 4. Analyze Images
        if image_urls:
            item.status = "analyzing_images"
            db.commit()
            all_image_analysis_results = []
            # Note: This part is still synchronous within the task.
            # For true async image fetching, one would use libraries like aiohttp within the task.
            for img_url in image_urls:
                temp_img_path = None
                try:
                    response = httpx.get(img_url, timeout=10)
                    response.raise_for_status()
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_img_file:
                        temp_img_file.write(response.content)
                        temp_img_path = temp_img_file.name
                    analysis = analyze_image_for_hallmarks(temp_img_path)
                    all_image_analysis_results.append({"image_url": img_url, "analysis": analysis})
                except Exception as e:
                    logger.error(f"Error analyzing image {img_url}: {e}")
                finally:
                    if temp_img_path and os.path.exists(temp_img_path):
                        os.remove(temp_img_path)
            item.image_analysis_results = json.dumps(all_image_analysis_results)

        # 5. Calculate ROI
        if extracted_weight_grams is not None and extracted_purity is not None:
            item.status = "calculating_roi"
            db.commit()
            try:
                roi_analysis_result = calculate_roi(
                    weight_grams=extracted_weight_grams,
                    purity=extracted_purity,
                    purchase_price=0  # Placeholder
                )
                item.roi_analysis = json.dumps(roi_analysis_result)
            except Exception as e:
                logger.error(f"Error calculating ROI: {e}")

        item.status = "completed"
        db.commit()
        logger.info(f"Successfully processed item {item_id}")

    except Exception as e:
        logger.error(f"An error occurred while processing item {item_id}: {e}")
        item.status = "failed"
        db.commit()
    finally:
        db.close()
