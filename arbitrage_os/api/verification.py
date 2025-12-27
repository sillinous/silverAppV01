import os
import shutil
from fastapi import APIRouter, UploadFile, File

from arbitrage_os.verification.image_analyzer import analyze_image_for_hallmarks

router = APIRouter()

@router.post("/analyze_image/")
async def analyze_image_endpoint(file: UploadFile = File(...)):
    """
    Endpoint to analyze an image for silver hallmarks.
    """
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        analysis = analyze_image_for_hallmarks(temp_path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
    return analysis
