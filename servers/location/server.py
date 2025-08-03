import os
import json
from typing import List, Dict, Optional, Any
from mcp_kit import ProxyMCP, Tool
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()

# --- Models ---
class PlaceInfo(BaseModel):
    id: str
    name: str
    type: str  # "city", "county", "state", "country"
    coordinates: Optional[Dict[str, float]]
    parent_place: Optional[str]
    historical_names: List[str]
    current_names: List[str]

class PlaceSearchResult(BaseModel):
    query: str
    results: List[PlaceInfo]
    confidence: float
    suggestions: List[str]

class GeographicContext(BaseModel):
    place_id: str
    time_period: str
    historical_context: str
    population_data: Optional[Dict]
    migration_patterns: List[str]
    significant_events: List[str]

# --- Stubbed place data ---
PLACE_DATABASE = {
    "new_york": {
        "id": "new_york",
        "name": "New York",
        "type": "state",
        "coordinates": {"lat": 42.1657, "lng": -74.9481},
        "parent_place": "united_states",
        "historical_names": ["New Netherland", "New York Colony"],
        "current_names": ["New York", "NY", "Empire State"]
    },
    "albany": {
        "id": "albany",
        "name": "Albany",
        "type": "city",
        "coordinates": {"lat": 42.6526, "lng": -73.7562},
        "parent_place": "new_york",
        "historical_names": ["Beverwyck", "Fort Orange"],
        "current_names": ["Albany", "Capital City"]
    },
    "albany_county": {
        "id": "albany_county",
        "name": "Albany County",
        "type": "county",
        "coordinates": {"lat": 42.6000, "lng": -73.9700},
        "parent_place": "new_york",
        "historical_names": ["Albany County"],
        "current_names": ["Albany County"]
    },
    "united_states": {
        "id": "united_states",
        "name": "United States",
        "type": "country",
        "coordinates": {"lat": 39.8283, "lng": -98.5795},
        "parent_place": None,
        "historical_names": ["Thirteen Colonies", "United Colonies"],
        "current_names": ["United States", "USA", "America"]
    }
}

# --- Tool Implementations ---
async def search_places(query: str, place_type: Optional[str] = None) -> PlaceSearchResult:
    """Search for places by name or partial match."""
    logger.info("Searching places", query=query, place_type=place_type)
    
    # TODO: Implement real place search
    # For now, search the stubbed database
    
    query_lower = query.lower()
    results = []
    
    for place_id, place_data in PLACE_DATABASE.items():
        # Check if query matches place name or historical names
        if (query_lower in place_data["name"].lower() or
            any(query_lower in name.lower() for name in place_data["historical_names"]) or
            any(query_lower in name.lower() for name in place_data["current_names"])):
            
            # Filter by place type if specified
            if place_type and place_data["type"] != place_type:
                continue
            
            results.append(PlaceInfo(**place_data))
    
    # Calculate confidence based on match quality
    confidence = 0.8 if results else 0.0
    
    # Generate suggestions for no results
    suggestions = []
    if not results:
        suggestions = [
            "Try searching for 'New York' or 'Albany'",
            "Check spelling of place names",
            "Try broader geographic terms"
        ]
    
    return PlaceSearchResult(
        query=query,
        results=results,
        confidence=confidence,
        suggestions=suggestions
    )

async def get_place_details(place_id: str) -> PlaceInfo:
    """Get detailed information about a specific place."""
    logger.info("Getting place details", place_id=place_id)
    
    if place_id not in PLACE_DATABASE:
        raise ValueError(f"Place {place_id} not found")
    
    place_data = PLACE_DATABASE[place_id]
    return PlaceInfo(**place_data)

async def get_geographic_context(place_id: str, time_period: str = "1850-1900") -> GeographicContext:
    """Get historical geographic context for a place and time period."""
    logger.info("Getting geographic context", place_id=place_id, time_period=time_period)
    
    if place_id not in PLACE_DATABASE:
        raise ValueError(f"Place {place_id} not found")
    
    place_data = PLACE_DATABASE[place_id]
    
    # TODO: Implement real historical context
    # For now, return stubbed context based on place and time period
    
    if place_id == "albany" and "1850" in time_period:
        context = GeographicContext(
            place_id=place_id,
            time_period=time_period,
            historical_context="Albany was a major transportation hub during the 1850s, with the Erie Canal connecting it to the Great Lakes and the Hudson River connecting it to New York City.",
            population_data={
                "1850": 50000,
                "1860": 62000,
                "1870": 69000
            },
            migration_patterns=[
                "Irish immigration following the Great Famine",
                "German immigration for economic opportunities",
                "Internal migration from rural areas"
            ],
            significant_events=[
                "Erie Canal completion (1825)",
                "Railroad expansion (1840s-1850s)",
                "Industrial growth and urbanization"
            ]
        )
    elif place_id == "new_york" and "1850" in time_period:
        context = GeographicContext(
            place_id=place_id,
            time_period=time_period,
            historical_context="New York State experienced rapid industrialization and urbanization during the mid-19th century, with significant population growth and economic development.",
            population_data={
                "1850": 3100000,
                "1860": 3900000,
                "1870": 4400000
            },
            migration_patterns=[
                "Massive European immigration",
                "Rural to urban migration",
                "Westward expansion"
            ],
            significant_events=[
                "Erie Canal completion (1825)",
                "Railroad expansion",
                "Industrial Revolution",
                "Civil War (1861-1865)"
            ]
        )
    else:
        context = GeographicContext(
            place_id=place_id,
            time_period=time_period,
            historical_context=f"General historical context for {place_data['name']} during {time_period}.",
            population_data=None,
            migration_patterns=["General migration patterns"],
            significant_events=["Historical events of the period"]
        )
    
    return context

async def normalize_place_name(place_name: str, time_period: Optional[str] = None) -> Dict[str, Any]:
    """Normalize a place name to standard format and identify historical variations."""
    logger.info("Normalizing place name", place_name=place_name, time_period=time_period)
    
    # TODO: Implement real place name normalization
    # For now, return stubbed normalization
    
    place_name_lower = place_name.lower()
    
    # Check if it matches any known places
    for place_id, place_data in PLACE_DATABASE.items():
        if (place_name_lower in place_data["name"].lower() or
            any(place_name_lower in name.lower() for name in place_data["historical_names"]) or
            any(place_name_lower in name.lower() for name in place_data["current_names"])):
            
            return {
                "original_name": place_name,
                "normalized_name": place_data["name"],
                "place_id": place_id,
                "place_type": place_data["type"],
                "historical_variations": place_data["historical_names"],
                "current_variations": place_data["current_names"],
                "confidence": 0.9
            }
    
    # If no exact match, return general normalization
    return {
        "original_name": place_name,
        "normalized_name": place_name.title(),
        "place_id": None,
        "place_type": "unknown",
        "historical_variations": [],
        "current_variations": [place_name.title()],
        "confidence": 0.5
    }

async def get_place_hierarchy(place_id: str) -> List[Dict[str, Any]]:
    """Get the hierarchical structure of a place (country -> state -> county -> city)."""
    logger.info("Getting place hierarchy", place_id=place_id)
    
    if place_id not in PLACE_DATABASE:
        raise ValueError(f"Place {place_id} not found")
    
    place_data = PLACE_DATABASE[place_id]
    hierarchy = []
    
    # Build hierarchy from current place up to country
    current_place = place_data
    while current_place:
        hierarchy.append({
            "id": current_place["id"],
            "name": current_place["name"],
            "type": current_place["type"],
            "coordinates": current_place["coordinates"]
        })
        
        # Move up to parent place
        if current_place["parent_place"] and current_place["parent_place"] in PLACE_DATABASE:
            current_place = PLACE_DATABASE[current_place["parent_place"]]
        else:
            current_place = None
    
    # Reverse to show from country down to specific place
    hierarchy.reverse()
    return hierarchy

async def suggest_related_places(place_id: str, relationship_type: str = "nearby") -> List[Dict[str, Any]]:
    """Suggest places related to the given place."""
    logger.info("Suggesting related places", place_id=place_id, relationship_type=relationship_type)
    
    if place_id not in PLACE_DATABASE:
        raise ValueError(f"Place {place_id} not found")
    
    place_data = PLACE_DATABASE[place_id]
    
    # TODO: Implement real place relationship suggestions
    # For now, return stubbed suggestions based on place type
    
    suggestions = []
    
    if place_data["type"] == "city":
        # Suggest nearby cities and the county
        for other_place_id, other_place in PLACE_DATABASE.items():
            if (other_place_id != place_id and 
                other_place["parent_place"] == place_data["parent_place"]):
                suggestions.append({
                    "place_id": other_place_id,
                    "name": other_place["name"],
                    "type": other_place["type"],
                    "relationship": "same_parent",
                    "distance": "unknown"
                })
    elif place_data["type"] == "county":
        # Suggest cities in the county
        for other_place_id, other_place in PLACE_DATABASE.items():
            if (other_place["parent_place"] == place_id):
                suggestions.append({
                    "place_id": other_place_id,
                    "name": other_place["name"],
                    "type": other_place["type"],
                    "relationship": "contained_in",
                    "distance": "unknown"
                })
    elif place_data["type"] == "state":
        # Suggest major cities in the state
        for other_place_id, other_place in PLACE_DATABASE.items():
            if (other_place["parent_place"] == place_id and 
                other_place["type"] == "city"):
                suggestions.append({
                    "place_id": other_place_id,
                    "name": other_place["name"],
                    "type": other_place["type"],
                    "relationship": "contained_in",
                    "distance": "unknown"
                })
    
    return suggestions

async def validate_place_coordinates(place_id: str, coordinates: Dict[str, float]) -> Dict[str, Any]:
    """Validate that coordinates are within the expected range for a place."""
    logger.info("Validating place coordinates", place_id=place_id, coordinates=coordinates)
    
    if place_id not in PLACE_DATABASE:
        raise ValueError(f"Place {place_id} not found")
    
    place_data = PLACE_DATABASE[place_id]
    expected_coords = place_data.get("coordinates")
    
    if not expected_coords:
        return {
            "valid": False,
            "reason": "No expected coordinates available for this place",
            "suggested_coordinates": None
        }
    
    # Simple validation - check if coordinates are within reasonable range
    lat_diff = abs(coordinates["lat"] - expected_coords["lat"])
    lng_diff = abs(coordinates["lng"] - expected_coords["lng"])
    
    # Allow for some variation (roughly 1 degree)
    is_valid = lat_diff < 1.0 and lng_diff < 1.0
    
    return {
        "valid": is_valid,
        "reason": "Coordinates within expected range" if is_valid else "Coordinates outside expected range",
        "expected_coordinates": expected_coords,
        "provided_coordinates": coordinates,
        "difference": {
            "latitude": lat_diff,
            "longitude": lng_diff
        },
        "suggested_coordinates": expected_coords if not is_valid else None
    }

# --- MCP Server Setup ---
proxy = ProxyMCP()

proxy.add_tool(Tool(
    name="search_places",
    description="Search for places by name or partial match.",
    fn=search_places,
    input_model=BaseModel.construct(__fields__={
        'query': (str, ...),
        'place_type': (Optional[str], None)
    }),
    output_model=PlaceSearchResult
))

proxy.add_tool(Tool(
    name="get_place_details",
    description="Get detailed information about a specific place.",
    fn=get_place_details,
    input_model=BaseModel.construct(__fields__={
        'place_id': (str, ...)
    }),
    output_model=PlaceInfo
))

proxy.add_tool(Tool(
    name="get_geographic_context",
    description="Get historical geographic context for a place and time period.",
    fn=get_geographic_context,
    input_model=BaseModel.construct(__fields__={
        'place_id': (str, ...),
        'time_period': (str, "1850-1900")
    }),
    output_model=GeographicContext
))

proxy.add_tool(Tool(
    name="normalize_place_name",
    description="Normalize a place name to standard format and identify historical variations.",
    fn=normalize_place_name,
    input_model=BaseModel.construct(__fields__={
        'place_name': (str, ...),
        'time_period': (Optional[str], None)
    }),
    output_model=Dict[str, Any]
))

proxy.add_tool(Tool(
    name="get_place_hierarchy",
    description="Get the hierarchical structure of a place (country -> state -> county -> city).",
    fn=get_place_hierarchy,
    input_model=BaseModel.construct(__fields__={
        'place_id': (str, ...)
    }),
    output_model=List[Dict[str, Any]]
))

proxy.add_tool(Tool(
    name="suggest_related_places",
    description="Suggest places related to the given place.",
    fn=suggest_related_places,
    input_model=BaseModel.construct(__fields__={
        'place_id': (str, ...),
        'relationship_type': (str, "nearby")
    }),
    output_model=List[Dict[str, Any]]
))

proxy.add_tool(Tool(
    name="validate_place_coordinates",
    description="Validate that coordinates are within the expected range for a place.",
    fn=validate_place_coordinates,
    input_model=BaseModel.construct(__fields__={
        'place_id': (str, ...),
        'coordinates': (Dict[str, float], ...)
    }),
    output_model=Dict[str, Any]
))

if __name__ == '__main__':
    logger.info("Starting Location MCP server...")
    proxy.run() 