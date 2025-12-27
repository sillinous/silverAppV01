import logging
import os
from openai import OpenAI
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

def geocode_address(address: str) -> dict:
    """
    Converts a string address into geographic coordinates (latitude and longitude).

    Args:
        address: The address string to geocode.

    Returns:
        A dictionary containing the latitude and longitude.
    """
    geolocator = Nominatim(user_agent="arbitrage_os")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    location = geocode(address)

    if location:
        return {"latitude": location.latitude, "longitude": location.longitude, "formatted_address": location.address}
    else:
        logger.warning(f"Geocoding failed for address: {address}")
        return {"latitude": None, "longitude": None, "formatted_address": None}

def cleanup_and_geocode(messy_address: str) -> dict:
    """
    Cleans up a messy address string using an LLM and then geocodes it.

    Requires the `OPENAI_API_KEY` environment variable.

    Args:
        messy_address: A potentially unstructured address.
        
    Returns:
        A dictionary with coordinates.
    """
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set.")
        raise ValueError("OPENAI_API_KEY environment variable not set.")

    client = OpenAI()
    
    system_prompt = """
    You are a geocoding expert. Your task is to convert a messy, unstructured, or colloquial address into a standard, machine-readable street address format that a geocoding API can understand.
    For example, if you receive 'Corner of 5th and Main, blue house', you should return something like '5th Street and Main Street'.
    Return only the cleaned address string and nothing else.
    """

    cleaned_address = messy_address.strip()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": messy_address},
            ],
            temperature=0,
        )
        cleaned_address = response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"LLM address cleaning failed: {e}. Falling back to original address.")
        # Fallback to the original address if LLM cleaning fails
        pass

    return geocode_address(cleaned_address)
