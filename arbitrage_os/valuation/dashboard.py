import logging
import os
import requests

logger = logging.getLogger(__name__)

def get_silver_spot_price() -> dict:
    """
    Fetches the current spot price of silver (XAG) from the Metals-API.

    This function requires a Metals-API key to be set in the environment
    as `METALS_API_KEY`.

    Returns:
        A dictionary containing the spot price data or an error message.
    """
    api_key = os.getenv("METALS_API_KEY")
    if not api_key:
        logger.error("METALS_API_KEY environment variable not set.")
        raise ValueError("METALS_API_KEY environment variable not set.")

    base_url = "https://www.metals-api.com/api/latest"
    params = {
        "access_key": api_key,
        "base": "USD",
        "symbols": "XAG"  # Silver
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching silver spot price: {e}")
        return {"error": str(e)}

def calculate_roi(weight_grams: float, purity: float, purchase_price: float) -> dict:
    """
    Calculates the potential ROI for a silver item.

    Args:
        weight_grams: The weight of the item in grams.
        purity: The purity of the silver (e.g., 0.925 for sterling).
        purchase_price: The price the item was purchased for.

    Returns:
        A dictionary with the calculated ROI details.
    """
    spot_price_data = get_silver_spot_price()
    if "error" in spot_price_data or not spot_price_data.get("rates"):
        logger.error("Could not retrieve silver spot price for ROI calculation.")
        return {"error": "Could not retrieve silver spot price."}

    # The API returns the price per ounce, so we need to convert grams to ounces
    # 1 gram = 0.0321507 troy ounces
    grams_to_troy_ounce = 0.0321507
    price_per_gram = spot_price_data["rates"]["XAG"] * grams_to_troy_ounce

    # Calculate the value of the silver content
    silver_value = weight_grams * purity * price_per_gram
    
    # Assume a refining fee of 15%
    refining_fee = silver_value * 0.15
    max_buy_price = silver_value - refining_fee
    
    profit = max_buy_price - purchase_price
    roi = (profit / purchase_price) * 100 if purchase_price > 0 else float('inf')

    return {
        "spot_price_per_ounce": spot_price_data["rates"]["XAG"],
        "item_silver_value": silver_value,
        "max_buy_price": max_buy_price,
        "profit": profit,
        "roi_percent": roi
    }
