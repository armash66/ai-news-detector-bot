"""Named Entity Recognition — extracts people, orgs, locations from text."""

import logging
from typing import List, Dict, Any, Optional

from src.config.settings import settings

logger = logging.getLogger("truthlens.nlp.ner")

# Lazy-loaded spaCy model
_nlp = None


def _get_nlp():
    """Lazy-load the spaCy NLP model."""
    global _nlp
    if _nlp is None:
        try:
            import spacy
            _nlp = spacy.load(settings.SPACY_MODEL)
            logger.info(f"Loaded spaCy model: {settings.SPACY_MODEL}")
        except OSError:
            logger.warning(f"spaCy model '{settings.SPACY_MODEL}' not found, attempting download...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", settings.SPACY_MODEL], check=True)
            import spacy
            _nlp = spacy.load(settings.SPACY_MODEL)
        except Exception as e:
            logger.error(f"Failed to load spaCy: {e}")
            raise
    return _nlp


class NERExtractor:
    """Extracts named entities from article text using spaCy."""

    # Entity types we care about for news intelligence
    RELEVANT_TYPES = {"PERSON", "ORG", "GPE", "LOC", "EVENT", "DATE", "NORP", "FAC"}

    def extract(self, text: str, max_length: int = 100000) -> List[Dict[str, Any]]:
        """
        Extract named entities from text.
        
        Returns:
            List of entity dicts: [{entity_text, entity_type, start, end, salience_score}]
        """
        if not text:
            return []

        # Truncate very long texts for spaCy performance
        if len(text) > max_length:
            text = text[:max_length]

        try:
            nlp = _get_nlp()
            doc = nlp(text)

            entities = []
            seen = set()  # Dedup entities within same text

            for ent in doc.ents:
                if ent.label_ not in self.RELEVANT_TYPES:
                    continue

                key = (ent.text.strip().lower(), ent.label_)
                if key in seen:
                    continue
                seen.add(key)

                # Compute simple salience based on length and frequency
                mention_count = text.lower().count(ent.text.lower())
                salience = min(1.0, mention_count * 0.2 + len(ent.text.split()) * 0.1)

                entities.append({
                    "entity_text": ent.text.strip(),
                    "entity_type": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "salience_score": round(salience, 3),
                })

            return sorted(entities, key=lambda e: e["salience_score"], reverse=True)

        except Exception as e:
            logger.error(f"NER extraction failed: {e}")
            return []

    def extract_locations(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter entities to only geographic locations (GPE, LOC, FAC)."""
        location_types = {"GPE", "LOC", "FAC"}
        return [e for e in entities if e["entity_type"] in location_types]

    def extract_people(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter entities to only people."""
        return [e for e in entities if e["entity_type"] == "PERSON"]

    def extract_organizations(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter entities to only organizations."""
        return [e for e in entities if e["entity_type"] == "ORG"]
