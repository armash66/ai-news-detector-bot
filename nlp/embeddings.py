"""Embedding Generator — produces dense vector representations using Sentence-BERT."""

import logging
from typing import List, Optional
import numpy as np

from src.config.settings import settings

logger = logging.getLogger("truthlens.nlp.embeddings")

# Lazy-loaded model instance
_model = None


def _get_model():
    """Lazy-load the sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info(f"Loaded embedding model: {settings.EMBEDDING_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise
    return _model


class EmbeddingGenerator:
    """Generates sentence embeddings for articles using Sentence-BERT."""

    def __init__(self):
        self.dimension = settings.EMBEDDING_DIMENSION

    def encode(self, text: str, max_length: int = 512) -> List[float]:
        """
        Encode a single text into an embedding vector.
        
        Args:
            text: Input text (will be truncated to max_length tokens)
            max_length: Maximum number of words to consider
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            return [0.0] * self.dimension

        # Truncate to approximate token limit
        words = text.split()
        if len(words) > max_length:
            text = " ".join(words[:max_length])

        try:
            model = _get_model()
            embedding = model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            return [0.0] * self.dimension

    def encode_batch(self, texts: List[str], batch_size: int = 32) -> List[List[float]]:
        """Encode multiple texts in batch for efficiency."""
        if not texts:
            return []

        try:
            model = _get_model()
            embeddings = model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            return [e.tolist() for e in embeddings]
        except Exception as e:
            logger.error(f"Batch embedding failed: {e}")
            return [[0.0] * self.dimension for _ in texts]

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two embedding vectors."""
        a = np.array(vec_a)
        b = np.array(vec_b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
