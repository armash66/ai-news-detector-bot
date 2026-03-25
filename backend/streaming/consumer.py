"""Redis Streams Consumer — reads messages from streams with consumer groups."""

import json
import logging
import time
from typing import Dict, Any, Callable, Optional, List, Tuple

import redis

from config.settings import settings

logger = logging.getLogger("truthlens.streaming.consumer")


class StreamConsumer:
    """Consumes messages from Redis Streams using consumer groups."""

    def __init__(self, group: str, consumer_name: str):
        self.group = group
        self.consumer_name = consumer_name
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

    def ensure_group(self, stream: str):
        """Create consumer group if it doesn't exist."""
        try:
            self.client.xgroup_create(stream, self.group, id="0", mkstream=True)
            logger.info(f"Created consumer group '{self.group}' on '{stream}'")
        except redis.ResponseError as e:
            if "BUSYGROUP" not in str(e):
                raise

    def consume(
        self,
        stream: str,
        handler: Callable[[Dict[str, Any]], bool],
        batch_size: int = 10,
        block_ms: int = 5000,
    ):
        """
        Blocking consume loop — reads messages and calls handler.
        
        Args:
            stream: Stream to consume from
            handler: Function that processes message data, returns True on success
            batch_size: Number of messages to read per batch
            block_ms: Block timeout in milliseconds
        """
        self.ensure_group(stream)
        logger.info(f"Consumer '{self.consumer_name}' listening on '{stream}' (group: {self.group})")

        while True:
            try:
                messages = self.client.xreadgroup(
                    self.group,
                    self.consumer_name,
                    {stream: ">"},
                    count=batch_size,
                    block=block_ms,
                )

                if not messages:
                    continue

                for stream_name, entries in messages:
                    for message_id, fields in entries:
                        try:
                            data = json.loads(fields.get("data", "{}"))
                            success = handler(data)

                            if success:
                                self.client.xack(stream, self.group, message_id)
                            else:
                                logger.warning(f"Handler returned failure for {message_id}")

                        except Exception as e:
                            logger.error(f"Error processing {message_id}: {e}")
                            # Message stays pending — will be redelivered

            except redis.ConnectionError:
                logger.warning("Redis connection lost, reconnecting in 5s...")
                self._client = None
                time.sleep(5)
            except Exception as e:
                logger.error(f"Consumer error: {e}")
                time.sleep(1)

    def get_pending_count(self, stream: str) -> int:
        """Get number of pending (unacknowledged) messages."""
        try:
            info = self.client.xpending(stream, self.group)
            return info.get("pending", 0) if isinstance(info, dict) else 0
        except Exception:
            return 0

    def close(self):
        if self._client:
            self._client.close()
            self._client = None
