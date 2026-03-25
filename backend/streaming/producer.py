"""Redis Streams Producer — publishes messages to streams."""

import json
import logging
from typing import Dict, Any, Optional

import redis

from config.settings import settings

logger = logging.getLogger("truthlens.streaming.producer")


class StreamProducer:
    """Publishes messages to Redis Streams."""

    def __init__(self):
        self._client: Optional[redis.Redis] = None

    @property
    def client(self) -> redis.Redis:
        if self._client is None:
            self._client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True,
            )
        return self._client

    def publish(self, stream: str, data: Dict[str, Any], max_len: int = 10000) -> str:
        """
        Publish a message to a Redis Stream.
        
        Args:
            stream: Stream name (use StreamTopics constants)
            data: Message payload (will be JSON-serialized)
            max_len: Max stream length (approximate trimming)
            
        Returns:
            Message ID assigned by Redis
        """
        try:
            payload = {"data": json.dumps(data)}
            message_id = self.client.xadd(stream, payload, maxlen=max_len, approximate=True)
            logger.debug(f"Published to {stream}: {message_id}")
            return message_id
        except redis.ConnectionError:
            logger.warning(f"Redis unavailable — message to {stream} dropped")
            return ""
        except Exception as e:
            logger.error(f"Failed to publish to {stream}: {e}")
            return ""

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
