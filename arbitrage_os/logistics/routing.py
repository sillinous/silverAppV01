import logging
import os
import httpx

logger = logging.getLogger(__name__)

def optimize_route(coordinates: list[dict]) -> dict:
    """
    Optimizes a route based on a list of geographic coordinates using the Mapbox Optimization API.

    This function requires a Mapbox API key to be set in the environment
    as `MAPBOX_API_KEY`.

    Args:
        coordinates: A list of dictionaries, each with "lat" and "lng" keys.

    Returns:
        A dictionary containing the optimized route information from Mapbox.
    """
    api_key = os.getenv("MAPBOX_API_KEY")
    if not api_key:
        logger.error("MAPBOX_API_KEY environment variable not set.")
        raise ValueError("MAPBOX_API_KEY environment variable not set.")

    if len(coordinates) < 2:
        raise ValueError("At least two coordinates are required for route optimization.")

    # Format coordinates into lng,lat;lng,lat string
    coords_str = ";".join([f"{coord['lng']},{coord['lat']}" for coord in coordinates])
    
    # Define the Mapbox API endpoint
    profile = "mapbox/driving"
    url = f"https://api.mapbox.com/optimized-trips/v1/{profile}/{coords_str}"

    params = {
        "access_token": api_key,
        "overview": "full",
        "steps": "true",
        "geometries": "geojson",
        "source": "first",
        "destination": "last",
        "roundtrip": "false" # Assuming it's a one-way trip from the first to the last point
    }

    try:
        with httpx.Client() as client:
            response = client.get(url, params=params)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            
            result = response.json()
            if result.get("code") != "Ok":
                logger.error(f"Mapbox API returned an error: {result.get('message')}")
                raise Exception(f"Mapbox API error: {result.get('message')}")

            # The 'trips' object contains the optimized route. We return the first trip.
            # The 'waypoints' object shows the original and optimized order of the coordinates.
            return result

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error occurred while calling Mapbox API: {e.response.text}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        raise