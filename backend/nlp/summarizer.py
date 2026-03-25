"""Summarizer — generates concise summaries at article and event level."""

import logging
import re
from typing import List

logger = logging.getLogger("truthlens.nlp.summarizer")

# Lazy-loaded model
_summarizer_model = None


class Summarizer:
    """Article and event summarization using extractive (default) or transformer models."""

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        """Generate a summary. Uses transformer if available, falls back to extractive."""
        if not text or len(text.split()) < 30:
            return text

        try:
            return self._transformer_summarize(text)
        except Exception as e:
            logger.debug(f"Transformer summarization unavailable, using extractive: {e}")
            return self._extractive_summarize(text, max_sentences)

    def _transformer_summarize(self, text: str) -> str:
        """Use HuggingFace BART/T5 for abstractive summarization."""
        global _summarizer_model
        if _summarizer_model is None:
            from transformers import pipeline
            _summarizer_model = pipeline(
                "summarization",
                model="sshleifer/distilbart-cnn-12-6",
                truncation=True,
            )

        # Truncate input (model limit ~1024 tokens)
        words = text.split()[:800]
        truncated = " ".join(words)

        result = _summarizer_model(
            truncated,
            max_length=130,
            min_length=30,
            do_sample=False,
        )
        return result[0]["summary_text"]

    def _extractive_summarize(self, text: str, max_sentences: int = 3) -> str:
        """Simple extractive summary — scores sentences by word frequency (TextRank-lite)."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        if len(sentences) <= max_sentences:
            return text

        # Score sentences based on word frequency
        word_freq = {}
        for sentence in sentences:
            for word in sentence.lower().split():
                word = re.sub(r'[^\w]', '', word)
                if len(word) > 3:
                    word_freq[word] = word_freq.get(word, 0) + 1

        scored = []
        for i, sentence in enumerate(sentences):
            score = sum(word_freq.get(re.sub(r'[^\w]', '', w.lower()), 0) for w in sentence.split())
            # Boost first sentence (usually contains the lede)
            if i == 0:
                score *= 1.5
            scored.append((score, i, sentence))

        scored.sort(reverse=True)
        top = sorted(scored[:max_sentences], key=lambda x: x[1])  # Maintain order

        return " ".join(s[2] for s in top)

    def summarize_event(self, article_summaries: List[str], max_sentences: int = 4) -> str:
        """Generate an event-level summary by combining multiple article summaries."""
        combined = " ".join(article_summaries)
        return self.summarize(combined, max_sentences)
