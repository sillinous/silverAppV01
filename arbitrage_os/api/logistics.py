from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from arbitrage_os.logistics.geocoding import cleanup_and_geocode
from arbitrage_os.logistics.routing import optimize_route

router = APIRouter()

class GeocodeRequest(BaseModel):
    address: str

class Coordinate(BaseModel):
    lat: float
    lng: float

class RouteRequest(BaseModel):
    coordinates: List[Coordinate]

class MultiGeocodeAndRouteRequest(BaseModel):
    addresses: List[str]


@router.post("/geocode/")
async def geocode_address_endpoint(request: GeocodeRequest):
    """
    Endpoint to geocode a given address string.
    """
    return cleanup_and_geocode(request.address)

@router.post("/geocode_and_optimize_route/")
async def geocode_and_optimize_route_endpoint(request: MultiGeocodeAndRouteRequest):
    """
    Endpoint to geocode multiple addresses and then optimize a route from them.
    """
    geocoded_coords = []
    failed_addresses = []
    
    for address in request.addresses:
        geocoded_data = cleanup_and_geocode(address)
        if geocoded_data and isinstance(geocoded_data, dict) and geocoded_data.get("lat") is not None and geocoded_data.get("lng") is not None:
            geocoded_coords.append(Coordinate(lat=geocoded_data["lat"], lng=geocoded_data["lng"]))
        else:
            failed_addresses.append(address)
            
    if not geocoded_coords:
        raise HTTPException(status_code=400, detail="No valid coordinates could be geocoded from the provided addresses.")

    optimized_route_result = optimize_route(geocoded_coords)
    
    return {
        "optimized_route": optimized_route_result,
        "failed_addresses": failed_addresses
    }

@router.post("/optimize_route/")
async def optimize_route_endpoint(request: RouteRequest):
    """
    Endpoint to optimize a route from a list of coordinates.
    """
    coords_list = [coord.dict() for coord in request.coordinates]
    return optimize_route(coords_list)
