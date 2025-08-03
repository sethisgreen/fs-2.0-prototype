"""
GEDCOM X utilities for FamilySearch API integration.

This module provides utilities for converting FamilySearch API responses
to standardized GEDCOM X format and vice versa.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
from pydantic import BaseModel


class GedcomXRecord(BaseModel):
    """GEDCOM X compliant record model."""
    id: str
    title: Optional[str] = None
    content: List[Dict[str, Any]] = []
    attribution: Optional[Dict[str, Any]] = None


class GedcomXPerson(BaseModel):
    """GEDCOM X compliant person model."""
    id: str
    names: List[Dict[str, Any]] = []
    facts: List[Dict[str, Any]] = []
    sources: List[Dict[str, Any]] = []
    relationships: List[Dict[str, Any]] = []


def convert_familysearch_to_gedcomx(fs_response: Dict[str, Any]) -> List[GedcomXRecord]:
    """
    Convert FamilySearch API response to GEDCOM X format.
    
    Args:
        fs_response: Raw FamilySearch API response
        
    Returns:
        List of GEDCOM X compliant records
    """
    records = []
    
    if "entries" not in fs_response:
        return records
    
    for entry in fs_response["entries"]:
        record = GedcomXRecord(
            id=entry.get("id", ""),
            title=entry.get("title", ""),
            content=entry.get("content", []),
            attribution=entry.get("attribution")
        )
        records.append(record)
    
    return records


def convert_gedcomx_to_standard_record(gedcomx_record: GedcomXRecord) -> Dict[str, Any]:
    """
    Convert GEDCOM X record to our standard record format.
    
    Args:
        gedcomx_record: GEDCOM X compliant record
        
    Returns:
        Standardized record dictionary
    """
    # Extract person information from GEDCOM X content
    persons = []
    for content_item in gedcomx_record.content:
        if content_item.get("type") == "http://gedcomx.org/v1/Person":
            persons.extend(content_item.get("persons", []))
    
    # Extract basic information from the first person
    person_info = {}
    if persons:
        person = persons[0]
        person_info = {
            "id": person.get("id", ""),
            "name": extract_person_name(person),
            "birthDate": extract_fact_value(person, "http://gedcomx.org/v1/Birth"),
            "deathDate": extract_fact_value(person, "http://gedcomx.org/v1/Death"),
            "residencePlace": extract_fact_value(person, "http://gedcomx.org/v1/Residence"),
        }
    
    return {
        "id": gedcomx_record.id,
        "name": person_info.get("name", ""),
        "birthDate": person_info.get("birthDate"),
        "deathDate": person_info.get("deathDate"),
        "residencePlace": person_info.get("residencePlace"),
        "recordUrl": f"https://familysearch.org/records/{gedcomx_record.id}",
        "fsId": gedcomx_record.id,
        "sourceDescriptions": extract_source_descriptions(gedcomx_record),
        "persons": persons,
        "relationships": extract_relationships(gedcomx_record)
    }


def extract_person_name(person: Dict[str, Any]) -> str:
    """Extract formatted name from GEDCOM X person."""
    names = person.get("names", [])
    if not names:
        return ""
    
    # Get the first name
    name = names[0]
    name_form = name.get("nameForms", [{}])[0]
    full_text = name_form.get("fullText", "")
    
    if full_text:
        return full_text
    
    # Fallback to constructing from parts
    parts = name_form.get("parts", [])
    given_name = ""
    surname = ""
    
    for part in parts:
        if part.get("type") == "http://gedcomx.org/v1/Given":
            given_name = part.get("value", "")
        elif part.get("type") == "http://gedcomx.org/v1/Surname":
            surname = part.get("value", "")
    
    return f"{given_name} {surname}".strip()


def extract_fact_value(person: Dict[str, Any], fact_type: str) -> Optional[str]:
    """Extract value from a specific fact type."""
    facts = person.get("facts", [])
    for fact in facts:
        if fact.get("type") == fact_type:
            return fact.get("value")
    return None


def extract_source_descriptions(record: GedcomXRecord) -> List[Dict[str, Any]]:
    """Extract source descriptions from GEDCOM X record."""
    sources = []
    for content_item in record.content:
        if content_item.get("type") == "http://gedcomx.org/v1/Record":
            sources.extend(content_item.get("sourceDescriptions", []))
    return sources


def extract_relationships(record: GedcomXRecord) -> List[Dict[str, Any]]:
    """Extract relationships from GEDCOM X record."""
    relationships = []
    for content_item in record.content:
        if content_item.get("type") == "http://gedcomx.org/v1/Record":
            relationships.extend(content_item.get("relationships", []))
    return relationships


def create_gedcomx_search_request(
    given_name: str,
    surname: str,
    year: Optional[int] = None,
    place: Optional[str] = None,
    max_results: int = 20
) -> Dict[str, Any]:
    """
    Create a GEDCOM X compliant search request.
    
    Args:
        given_name: First name
        surname: Last name
        year: Year to search
        place: Place to search
        max_results: Maximum number of results
        
    Returns:
        GEDCOM X compliant search request
    """
    request = {
        "query": {
            "persons": [{
                "names": [{
                    "nameForms": [{
                        "parts": [
                            {"type": "http://gedcomx.org/v1/Given", "value": given_name},
                            {"type": "http://gedcomx.org/v1/Surname", "value": surname}
                        ]
                    }]
                }]
            }]
        },
        "count": max_results
    }
    
    # Add date constraint if provided
    if year:
        request["query"]["persons"][0]["facts"] = [{
            "type": "http://gedcomx.org/v1/Birth",
            "date": {
                "original": str(year),
                "formal": f"+{year}"
            }
        }]
    
    # Add place constraint if provided
    if place:
        if "facts" not in request["query"]["persons"][0]:
            request["query"]["persons"][0]["facts"] = []
        request["query"]["persons"][0]["facts"].append({
            "type": "http://gedcomx.org/v1/Residence",
            "place": {
                "original": place
            }
        })
    
    return request


def validate_gedcomx_response(response: Dict[str, Any]) -> bool:
    """
    Validate that a response follows GEDCOM X format.
    
    Args:
        response: API response to validate
        
    Returns:
        True if valid GEDCOM X format
    """
    try:
        # Basic structure validation
        if "entries" not in response:
            return False
        
        for entry in response["entries"]:
            if "id" not in entry:
                return False
            
            # Validate content structure
            if "content" in entry:
                for content_item in entry["content"]:
                    if "type" not in content_item:
                        return False
        
        return True
    except Exception:
        return False


def create_attribution(contributor: str = "FS 2.0 Prototype") -> Dict[str, Any]:
    """Create a standard attribution for GEDCOM X records."""
    return {
        "contributor": {
            "resourceId": contributor
        },
        "modified": datetime.utcnow().isoformat() + "Z"
    } 