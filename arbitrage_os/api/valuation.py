from fastapi import APIRouter
from pydantic import BaseModel

from arbitrage_os.valuation.dashboard import calculate_roi

router = APIRouter()

class RoiRequest(BaseModel):
    weight_grams: float
    purity: float
    purchase_price: float

@router.post("/calculate_roi/")
async def calculate_roi_endpoint(request: RoiRequest):
    """
    Endpoint to calculate ROI for a silver item.
    """
    return calculate_roi(
        weight_grams=request.weight_grams,
        purity=request.purity,
        purchase_price=request.purchase_price
    )
