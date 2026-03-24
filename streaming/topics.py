"""Stream topic definitions for the Redis Streams messaging layer."""


class StreamTopics:
    """Central registry of all stream/topic names."""

    # Ingestion → NLP Pipeline
    RAW_ARTICLES = "stream:raw_articles"

    # NLP Pipeline → Event Detection
    PROCESSED_ARTICLES = "stream:processed_articles"

    # Event Detection → Trust Engine, Alert System
    EVENT_UPDATES = "stream:event_updates"

    # Alert System → API/WebSocket
    ALERTS = "stream:alerts"

    # Failed messages for reprocessing
    DEAD_LETTER = "stream:dead_letter"


# Consumer group names
class ConsumerGroups:
    NLP_WORKERS = "nlp_workers"
    EVENT_WORKERS = "event_workers"
    TRUST_WORKERS = "trust_workers"
    ALERT_WORKERS = "alert_workers"
