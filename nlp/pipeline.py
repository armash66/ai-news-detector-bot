"""NLP Pipeline Orchestrator — chains all NLP modules in sequence."""

import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from src.nlp.preprocessor import TextPreprocessor, CleanedText
from src.nlp.embeddings import EmbeddingGenerator
from src.nlp.ner import NERExtractor
from src.nlp.sentiment import SentimentAnalyzer
from src.nlp.summarizer import Summarizer
from src.nlp.geo_extractor import GeoExtractor
from src.nlp.fake_news import FakeNewsClassifier

logger = logging.getLogger("truthlens.nlp.pipeline")


@dataclass
class NLPResult:
    """Complete NLP processing output for a single article."""
    clean_text: str = ""
    language: str = "en"
    word_count: int = 0
    embedding: List[float] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    locations: List[Dict[str, Any]] = field(default_factory=list)
    sentiment_score: float = 0.0
    bias_score: float = 0.0
    summary: str = ""
    fake_news_result: Optional[Dict[str, Any]] = None


class NLPPipeline:
    """
    Orchestrates the full NLP pipeline:
    Clean → Embed → NER → Sentiment → Summarize → Geo → FakeNews
    """

    def __init__(self):
        self.preprocessor = TextPreprocessor()
        self.embedder = EmbeddingGenerator()
        self.ner = NERExtractor()
        self.sentiment = SentimentAnalyzer()
        self.summarizer = Summarizer()
        self.geo_extractor = GeoExtractor()
        self.fake_news = FakeNewsClassifier()
        logger.info("NLP Pipeline initialized with all modules")

    def process(
        self,
        raw_text: str,
        source_reliability: float = 0.5,
        has_author: bool = True,
    ) -> NLPResult:
        """
        Run the full NLP pipeline on raw article text.
        
        Args:
            raw_text: Raw article content
            source_reliability: Source credibility score (0-1)
            has_author: Whether the article has named authorship
            
        Returns:
            NLPResult with all extracted intelligence
        """
        result = NLPResult()

        # Step 1: Clean text
        cleaned: CleanedText = self.preprocessor.clean(raw_text)
        result.clean_text = cleaned.text
        result.language = cleaned.language
        result.word_count = cleaned.word_count

        if not cleaned.text:
            logger.warning("Empty text after preprocessing, skipping remaining pipeline")
            return result

        # Step 2: Generate embedding
        result.embedding = self.embedder.encode(cleaned.text)

        # Step 3: Extract named entities
        result.entities = self.ner.extract(cleaned.text)

        # Step 4: Extract locations from entities
        result.locations = self.geo_extractor.extract(result.entities)

        # Step 5: Sentiment analysis
        sentiment_result = self.sentiment.analyze(cleaned.text)
        result.sentiment_score = sentiment_result.compound
        result.bias_score = self.sentiment.compute_bias_score(cleaned.text)

        # Step 6: Summarize
        result.summary = self.summarizer.summarize(cleaned.text)

        # Step 7: Fake news classification
        result.fake_news_result = self.fake_news.classify(
            cleaned.text,
            source_reliability=source_reliability,
            has_author=has_author,
        )

        logger.debug(
            f"Pipeline complete: {result.word_count} words, "
            f"{len(result.entities)} entities, "
            f"sentiment={result.sentiment_score:.2f}"
        )

        return result
