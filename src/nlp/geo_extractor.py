"""Geo Extractor — extracts and geocodes locations from NER output."""

import logging
from typing import List, Dict, Any

logger = logging.getLogger("truthlens.nlp.geo_extractor")

# Cache of known locations to avoid repeated API calls
_location_cache: Dict[str, Dict[str, Any]] = {}


class GeoExtractor:
    """Extracts geographic coordinates from entity mentions."""

    # Well-known locations (avoids geocoding API for common places)
    KNOWN_LOCATIONS = {
        "united states": {"name": "United States", "lat": 39.83, "lon": -98.58, "country": "US"},
        "china": {"name": "China", "lat": 35.86, "lon": 104.19, "country": "CN"},
        "russia": {"name": "Russia", "lat": 61.52, "lon": 105.32, "country": "RU"},
        "ukraine": {"name": "Ukraine", "lat": 48.38, "lon": 31.17, "country": "UA"},
        "india": {"name": "India", "lat": 20.59, "lon": 78.96, "country": "IN"},
        "london": {"name": "London", "lat": 51.51, "lon": -0.13, "country": "GB"},
        "washington": {"name": "Washington D.C.", "lat": 38.91, "lon": -77.04, "country": "US"},
        "beijing": {"name": "Beijing", "lat": 39.90, "lon": 116.40, "country": "CN"},
        "moscow": {"name": "Moscow", "lat": 55.76, "lon": 37.62, "country": "RU"},
        "gaza": {"name": "Gaza", "lat": 31.50, "lon": 34.47, "country": "PS"},
        "jerusalem": {"name": "Jerusalem", "lat": 31.77, "lon": 35.23, "country": "IL"},
        "kyiv": {"name": "Kyiv", "lat": 50.45, "lon": 30.52, "country": "UA"},
        "paris": {"name": "Paris", "lat": 48.86, "lon": 2.35, "country": "FR"},
        "tokyo": {"name": "Tokyo", "lat": 35.68, "lon": 139.69, "country": "JP"},
        "new york": {"name": "New York", "lat": 40.71, "lon": -74.01, "country": "US"},
        "berlin": {"name": "Berlin", "lat": 52.52, "lon": 13.40, "country": "DE"},
        "israel": {"name": "Israel", "lat": 31.05, "lon": 34.85, "country": "IL"},
        "iran": {"name": "Iran", "lat": 32.43, "lon": 53.69, "country": "IR"},
        "syria": {"name": "Syria", "lat": 34.80, "lon": 38.99, "country": "SY"},
        "taiwan": {"name": "Taiwan", "lat": 23.70, "lon": 120.96, "country": "TW"},
    }

    def extract(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extract geocoded locations from NER entities.
        
        Args:
            entities: NER output with entity_type GPE/LOC/FAC
            
        Returns:
            List of location dicts: [{name, lat, lon, country, confidence}]
        """
        location_types = {"GPE", "LOC", "FAC"}
        location_entities = [e for e in entities if e.get("entity_type") in location_types]

        results = []
        seen = set()

        for entity in location_entities:
            name = entity["entity_text"]
            key = name.lower().strip()

            if key in seen:
                continue
            seen.add(key)

            # Check known locations first
            if key in self.KNOWN_LOCATIONS:
                loc = self.KNOWN_LOCATIONS[key].copy()
                loc["confidence"] = 0.95
                results.append(loc)
            elif key in _location_cache:
                results.append(_location_cache[key].copy())
            else:
                # Fallback: store without coordinates (can be geocoded later)
                loc = {"name": name, "lat": None, "lon": None, "country": None, "confidence": 0.3}
                _location_cache[key] = loc
                results.append(loc)

        return results
