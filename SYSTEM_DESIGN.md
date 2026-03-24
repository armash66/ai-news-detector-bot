# TruthLens v3 — Real-Time News Detection & Intelligence Platform

## System Design Document

---

# 1. Project Vision

**TruthLens** is a **Real-Time News Detection and Intelligence Platform** — a backend-heavy, AI-powered system that continuously ingests global news from hundreds of sources, detects emerging events before they trend, organizes information into structured event entities, and enriches every datapoint with NLP-driven intelligence.

### What Problem It Solves

Traditional news aggregators (Google News, Apple News) show you articles. They don't tell you:
- *When* an event started and *how* it's evolving
- *Which* claims across sources contradict each other
- *Whether* the source reporting it is trustworthy
- *What* entities, locations, and actors are involved
- *How* narratives are spreading — organically or through coordinated amplification

TruthLens solves the **intelligence gap** between raw news and actionable understanding.

### Why It's Different From a News App

| Dimension | News Aggregator | TruthLens |
|---|---|---|
| Core unit | Article | **Event** |
| Organization | Category/topic | **Dynamic event clusters** |
| Analysis | None | **NLP: NER, sentiment, trust, claims** |
| Trust | Implicit reputation | **Computed credibility scores** |
| Fake news | None | **Sub-feature with explainability** |
| Timeline | Chronological feed | **Event lifecycle tracking** |
| Search | Keyword match | **Semantic + trust-aware ranking** |

### Why It's a Strong Project

This is a **systems engineering + AI/ML converged project** that demonstrates:
- Distributed systems design (streaming, queues, async workers)
- Real-time data pipeline architecture
- Production NLP (not toy models)
- Event-driven architecture
- Multi-database polyglot persistence
- Trust/safety engineering with explainability

---

# 2. Core Objective

## Primary Goal
**Detect real-world events from raw article streams, organize all related information around those events, and enrich them with AI-extracted intelligence.**

## Why Event-Centric Modeling

Articles are **fragments**. A single real-world event (e.g., an earthquake, a policy change, a military operation) generates hundreds of articles across many sources over days or weeks.

An article-centric system makes you read 50 articles about the same thing. An **event-centric** system says: "Here is one event. Here are 50 sources covering it. Here's how it evolved. Here's where the sources disagree."

**Event-centric modeling enables:**
1. **Deduplication at the semantic level** — not URL dedup, but meaning dedup
2. **Cross-source validation** — compare claims from 10+ sources automatically
3. **Lifecycle tracking** — events have a birth, evolution, peak, and decay
4. **Contradiction detection** — requires multiple articles mapped to the same event
5. **Trend analysis** — track how fast an event cluster grows
6. **Alert generation** — trigger on event significance, not individual articles

---

# 3. Complete Feature Set

## 3.1 Core System Features
- **Multi-source ingestion**: RSS, NewsAPI, GDELT, web scraping — modular connectors with retries and rate limiting
- **Article normalization**: Clean, structure, and standardize raw input from any source into a uniform schema
- **Deduplication**: URL-level, title-level (fuzzy), and semantic-level (embedding similarity > threshold)
- **Event detection**: Cluster incoming articles into events using embedding similarity + temporal proximity
- **Event lifecycle management**: Track event creation, growth, peak, decline. Support merge (two events are actually one) and split (one event forks into sub-events)
- **Event timelines**: Ordered sequence of developments within an event
- **Real-time streaming**: Pub/sub for live updates to connected consumers

## 3.2 AI/NLP Features
- **Text preprocessing**: Language detection, boilerplate removal, sentence splitting
- **Embedding generation**: Sentence-BERT embeddings for every article, stored in vector DB for similarity search
- **Named Entity Recognition (NER)**: Extract people, organizations, locations, dates using spaCy
- **Summarization**: Generate concise event-level summaries by synthesizing across multiple articles
- **Sentiment analysis**: Per-article and per-event sentiment scores
- **Bias detection**: Detect left/right/center framing in article language
- **Geo-extraction**: Extract and geocode locations for map-based visualization

## 3.3 Intelligence Features
- **Trend detection**: Identify topics gaining velocity (article count acceleration, not just count)
- **Early signal detection**: Flag emerging clusters before they reach mainstream — low article count but high diversity of sources
- **Knowledge graph**: Entity-relation triples (Person → ORG, Location → Event) stored in graph DB
- **Entity linking**: Resolve "Biden", "President Biden", "POTUS" to the same entity node
- **Claim extraction**: Isolate factual assertions from article text for independent verification

## 3.4 Trust & Credibility Features
- **Source credibility scoring**: Historical accuracy, bias, transparency — scored 0-1
- **Article credibility scoring**: Composite of source score, language analysis, claim verification
- **Cross-source validation**: If 8/10 sources agree but 2 disagree, flag the outliers
- **Contradiction detection**: Identify mutually exclusive claims about the same event
- **Fake news classification**: Binary classifier (reliable/unreliable) with confidence — a sub-feature, not the focus
- **Propaganda detection**: Identify emotional manipulation, loaded language, logical fallacies
- **Explainability**: Every trust score comes with human-readable reasoning

## 3.5 Analytics Features
- **Event velocity tracking**: How fast is an event growing?
- **Source diversity metrics**: How many independent sources cover this event?
- **Geographic heat maps**: Where are events concentrated?
- **Narrative flow analysis**: How do talking points propagate across sources?
- **Topic distribution**: What categories dominate the current news cycle?

## 3.6 Advanced Features
- **Alert system**: Configurable triggers (new event above threshold, trust anomaly, trend spike)
- **Semantic search**: Find events by meaning, not just keywords
- **Multimodal analysis**: Image verification, deepfake detection (existing capability)
- **Event comparison**: Side-by-side analysis of how two events are covered
- **API webhooks**: Push notifications to external systems

---

# 4. Event-Centric Data Model

## 4.1 Why Events Are the Core Abstraction

```
Traditional: Source → Article → Display
TruthLens:   Source → Article → Event → Intelligence → Display
```

The **Event** is the central node. Everything else (articles, claims, entities, timelines) points to or through it. This enables:
- Aggregation (combine 50 articles into 1 event view)
- Comparison (how do different sources report the same event?)
- Tracking (how did this event evolve over time?)
- Scoring (trust score based on source diversity + claim consistency)

## 4.2 How Articles Map to Events

1. Article arrives and gets embeddings generated
2. Embedding is compared against existing event centroids
3. If cosine similarity > threshold (e.g., 0.78) AND temporal window matches → assign to existing event
4. If no match → create a new event with this article as the seed
5. Event centroid is recalculated as new articles join

## 4.3 How Events Evolve

Events have a **lifecycle**:
```
EMERGING → DEVELOPING → ONGOING → PEAKED → DECLINING → ARCHIVED
```

State transitions are driven by:
- **Article velocity**: New articles/hour
- **Source diversity**: Number of unique sources
- **Recency**: Time since last new article
- **Significance score**: Composite metric

## 4.4 Merge/Split Logic

**Merge**: Two events that are actually the same (e.g., "Earthquake in Turkey" and "Seismic activity in SE Turkey" converge). Triggered when event centroid similarity exceeds threshold after drift.

**Split**: An event forks (e.g., "Middle East conflict" splits into "Gaza ceasefire talks" and "Lebanon border tensions"). Triggered when intra-cluster variance exceeds threshold and subclusters emerge.

## 4.5 Detailed Schemas

### Source
```python
class Source:
    id: UUID
    domain: str              # "bbc.co.uk"
    name: str                # "BBC News"
    source_type: enum        # RSS, API, SCRAPER
    reliability_score: float # 0.0 - 1.0, computed
    bias_rating: str         # LEFT, CENTER_LEFT, CENTER, CENTER_RIGHT, RIGHT
    country: str             # ISO country code
    language: str            # ISO language code
    is_verified: bool
    metadata: JSON           # Additional source info
    created_at: datetime
    updated_at: datetime
```

### Raw Article
```python
class RawArticle:
    id: UUID
    source_id: FK → Source
    url: str (unique)
    raw_html: text           # Original HTML
    raw_text: text           # Extracted plaintext
    title: str
    author: str | null
    published_at: datetime
    fetched_at: datetime
    content_hash: str        # SHA-256 for dedup
    processing_status: enum  # PENDING, PROCESSING, DONE, FAILED
```

### Processed Article
```python
class ProcessedArticle:
    id: UUID
    raw_article_id: FK → RawArticle
    source_id: FK → Source
    event_id: FK → Event | null
    clean_text: text
    summary: text
    embedding_vector: vector(768) # Stored in vector DB
    language: str
    sentiment_score: float   # -1.0 to 1.0
    bias_score: float
    credibility_score: float # Composite
    word_count: int
    entities_extracted: JSON  # [{type, value, salience}]
    locations: JSON           # [{name, lat, lon}]
    topics: JSON              # [topic_labels]
    processed_at: datetime
```

### Event (Core Entity)
```python
class Event:
    id: UUID
    title: str                # AI-generated event title
    summary: text             # AI-generated multi-source summary
    category: str             # POLITICS, CONFLICT, ECONOMY, etc.
    status: enum              # EMERGING, DEVELOPING, ONGOING, PEAKED, DECLINING, ARCHIVED
    significance_score: float # 0-100
    trust_score: float        # 0-1, aggregate
    article_count: int        # Denormalized for fast queries
    source_count: int         # Number of unique sources
    first_seen_at: datetime
    last_updated_at: datetime
    peak_at: datetime | null
    centroid_embedding: vector(768) # Average embedding
    primary_location: JSON    # {name, lat, lon}
    primary_entities: JSON    # Top entities
    sentiment_distribution: JSON  # {positive: 0.3, negative: 0.5, neutral: 0.2}
    parent_event_id: FK → Event | null  # For split events
    merged_into_id: FK → Event | null   # For merged events
    metadata: JSON
```

### Claim
```python
class Claim:
    id: UUID
    event_id: FK → Event
    article_id: FK → ProcessedArticle
    claim_text: text
    claim_type: enum         # FACTUAL, OPINION, PREDICTION
    verdict: enum            # VERIFIED, FALSE, UNVERIFIED, DISPUTED
    confidence: float
    supporting_sources: int
    contradicting_sources: int
    evidence: JSON           # Links to corroborating/contradicting articles
    extracted_at: datetime
```

### Timeline Entry
```python
class TimelineEntry:
    id: UUID
    event_id: FK → Event
    timestamp: datetime
    description: text        # "Reuters reports earthquake magnitude 7.2"
    source_id: FK → Source
    article_id: FK → ProcessedArticle
    entry_type: enum         # INITIAL_REPORT, UPDATE, CORRECTION, ESCALATION
    significance: float
```

### Alert
```python
class Alert:
    id: UUID
    event_id: FK → Event | null
    alert_type: enum         # NEW_EVENT, TREND_SPIKE, TRUST_ANOMALY, CONTRADICTION
    severity: enum           # LOW, MEDIUM, HIGH, CRITICAL
    title: str
    description: text
    triggered_at: datetime
    acknowledged: bool
    metadata: JSON
```

### Entity (Knowledge Graph Node)
```python
class Entity:
    id: UUID
    canonical_name: str      # "Joe Biden"
    entity_type: enum        # PERSON, ORG, LOCATION, CONCEPT
    aliases: JSON            # ["Biden", "POTUS", "President Biden"]
    description: text
    wikidata_id: str | null
    metadata: JSON

class EntityMention:
    id: UUID
    entity_id: FK → Entity
    article_id: FK → ProcessedArticle
    event_id: FK → Event | null
    mention_text: str
    context_snippet: text
    salience_score: float
```

---

# 5. End-to-End System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                                 │
│  RSS Feeds │ News APIs │ Web Scrapers │ Social Media (future)    │
└──────┬────────┬──────────┬────────────┬──────────────────────────┘
       │        │          │            │
       ▼        ▼          ▼            ▼
┌─────────────────────────────────────────────────────────────────┐
│                   INGESTION LAYER                                │
│  Modular Connectors → Normalization → Dedup → Content Hash       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   STREAMING LAYER                                │
│  Redis Streams: raw_articles │ processed │ events │ alerts       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   NLP PIPELINE (Workers)                          │
│  Clean → Embed → NER → Sentiment → Geo → Summarize → Score      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   EVENT DETECTION ENGINE                          │
│  Clustering → Assignment → Merge/Split → Timeline → Status       │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   TRUST ENGINE                                    │
│  Source Score → Article Score → Cross-validation → Contradictions │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           ▼
┌──────────────┬────────────┬─────────────┬───────────────────────┐
│ PostgreSQL   │ Redis      │ Vector DB   │ Elasticsearch         │
│ (structured) │ (cache)    │ (embeddings)│ (full-text search)    │
└──────┬───────┴────────────┴─────────────┴───────────────────────┘
       │
       ▼
┌─────────────────────────────────────────────────────────────────┐
│                   API LAYER (FastAPI)                             │
│  /events │ /search │ /trending │ /analyze │ /trust │ /alerts     │
└─────────────────────────────────────────────────────────────────┘
```

**Data Flow Step-by-Step:**
1. **Ingest**: Connectors pull articles from RSS/APIs/scrapers on schedules
2. **Normalize**: Raw HTML/JSON → standardized `RawArticle` schema
3. **Deduplicate**: Content hash + URL check prevents duplicates
4. **Queue**: Validated raw articles published to `raw_articles` stream
5. **NLP Workers**: Consume stream → clean, embed, extract entities, score
6. **Store**: Processed article saved to PostgreSQL, embedding to vector DB
7. **Event Detection**: Compare embedding against existing event centroids
8. **Assign/Create**: Attach to existing event or create new one
9. **Trust Engine**: Score article and update event trust metrics
10. **Alert Check**: Evaluate alert rules against new event state
11. **Cache**: Hot events and trending data cached in Redis
12. **Serve**: API layer reads from PostgreSQL/cache/search index

---

# 6. Data Ingestion Design

## Connector Architecture

Each connector implements a base interface:

```python
class BaseConnector(ABC):
    @abstractmethod
    async def fetch(self) -> List[RawArticleInput]: ...
    @abstractmethod
    async def health_check(self) -> bool: ...
```

### Connector Types

| Connector | Source | Frequency | Strategy |
|---|---|---|---|
| RSS | BBC, Reuters, NYT, Al Jazeera, etc. | Every 2-5 min | `feedparser` with ETag/304 support |
| NewsAPI | newsapi.org | Every 5 min | REST with API key rotation |
| GDELT | Global event stream | Every 15 min | Bulk CSV download + parse |
| Scraper | Custom targets | Every 10 min | `BeautifulSoup` + `httpx` with proxy rotation |

### Rate Limiting
- Per-source rate limits stored in config
- Token bucket algorithm for API sources
- Exponential backoff on `429` / `5xx` responses
- Circuit breaker: after 5 consecutive failures, pause source for 15 minutes

### Retry Strategy
- 3 retries with exponential backoff (1s, 4s, 16s)
- Dead letter queue for articles that fail all retries
- Periodic sweep of dead letter queue for reprocessing

### Deduplication
Three layers:
1. **URL exact match** — fastest, catches identical articles
2. **Content hash** — SHA-256 of normalized text, catches reposts
3. **Semantic similarity** — embedding cosine > 0.95, catches paraphrases (runs in NLP pipeline, not ingestion)

### Scaling
- Each connector runs as an independent async task
- New sources added via config/DB without code changes
- Connector pool scales horizontally — add more workers for more sources

---

# 7. Streaming / Queue Design

## Why Queues Are Needed

Without queues, a burst of 1,000 articles from GDELT would overwhelm the NLP pipeline (which is GPU-bound). Queues decouple:
- **Ingestion speed** (fast, I/O bound) from **processing speed** (slow, compute bound)
- Enable **independent scaling** of producers and consumers
- Provide **fault tolerance** — if NLP worker crashes, messages aren't lost

## Technology: Redis Streams

Redis Streams chosen over Kafka for MVP because:
- Already in the stack (used for caching)
- Supports consumer groups (Kafka-like semantics)
- Lower operational complexity than Kafka
- Sufficient throughput for ~10K articles/hour

**Migration path to Kafka** when needed: swap the `StreamProducer`/`StreamConsumer` implementations. The pipeline code doesn't change.

## Stream Topics

| Stream | Publisher | Consumer | Purpose |
|---|---|---|---|
| `raw_articles` | Ingestion | NLP Worker | Unprocessed articles |
| `processed_articles` | NLP Worker | Event Detector | Articles with embeddings + NER |
| `event_updates` | Event Detector | Trust Engine, Alert System | New/updated events |
| `alerts` | Alert System | API (WebSocket) | Real-time alerts |
| `dead_letter` | Any | Reprocessor | Failed messages |

## Consumer Groups
- Multiple NLP workers in one consumer group — messages are load-balanced
- Event detector and trust engine in separate groups — both receive all event_updates

## Failure Handling
- **Acknowledgment**: Messages only ACK'd after successful processing
- **Pending list**: Unacknowledged messages automatically redelivered after timeout
- **Idempotency**: Each article has a UUID; processing is idempotent (upsert, not insert)
- **Partitioning**: Articles can be partitioned by source domain for ordered processing

---

# 8. AI/NLP Pipeline (Detailed)

## 8.1 Text Preprocessing
- **Purpose**: Clean raw article text for downstream NLP
- **Input**: `RawArticle.raw_text`
- **Output**: `clean_text`, `language`, `word_count`
- **Logic**: Remove HTML tags, ads, navigation text, normalize unicode, detect language (using `langdetect`), strip boilerplate (using `trafilatura`-style extraction)
- **Model**: Heuristic + regex (no ML needed)
- **Tradeoff**: Speed over perfection — some noise is acceptable

## 8.2 Embedding Generation
- **Purpose**: Generate dense vector representation for similarity search and clustering
- **Input**: `clean_text` (first 512 tokens)
- **Output**: `vector(768)` — 768-dimensional float array
- **Model**: `all-MiniLM-L6-v2` (Sentence-BERT) — 80MB, fast inference
- **Where**: After preprocessing, before event detection
- **Tradeoff**: MiniLM is 5x faster than large BERT with ~95% of quality. Upgrade to `all-mpnet-base-v2` for production if GPU available

## 8.3 Named Entity Recognition (NER)
- **Purpose**: Extract PERSON, ORG, GPE, DATE, EVENT entities from text
- **Input**: `clean_text`
- **Output**: `[{entity_text, entity_type, start, end, salience_score}]`
- **Model**: spaCy `en_core_web_trf` (transformer-based) for accuracy, `en_core_web_sm` for speed
- **Where**: After preprocessing, feeds into knowledge graph
- **Tradeoff**: Transformer model is 10x slower but significantly more accurate on news text

## 8.4 Sentiment Analysis
- **Purpose**: Score positive/negative/neutral sentiment for bias analysis
- **Input**: `clean_text`
- **Output**: `{positive: float, negative: float, neutral: float, compound: float}`
- **Model**: `cardiffnlp/twitter-roberta-base-sentiment-latest` (HuggingFace) — fine-tuned for news-adjacent text
- **Tradeoff**: Model is general-purpose; for higher accuracy, fine-tune on news corpus

## 8.5 Summarization
- **Purpose**: Generate concise summaries at article and event level
- **Input**: Article: `clean_text`. Event: concatenated top-5 article summaries
- **Output**: 2-3 sentence summary
- **Model**: `facebook/bart-large-cnn` for extractive-abstractive hybrid
- **Where**: After event assignment (event summaries generated periodically)
- **Tradeoff**: BART is slow; use extractive (TextRank) for MVP, upgrade to BART for quality

## 8.6 Geo-Extraction
- **Purpose**: Extract geographic locations and coordinates for map features
- **Input**: NER output (GPE entities) + `clean_text`
- **Output**: `[{name, country, lat, lon, confidence}]`
- **Model**: spaCy NER + geocoding API (Nominatim/OpenStreetMap)
- **Tradeoff**: Geocoding API calls add latency; cache common locations in Redis

## 8.7 Fake News Classification (Sub-feature)
- **Purpose**: Flag potentially unreliable articles
- **Input**: `clean_text`, `source_reliability_score`, linguistic features
- **Output**: `{label: RELIABLE|UNRELIABLE, confidence: float, reasons: [str]}`
- **Model**: Fine-tuned RoBERTa on LIAR-PLUS dataset + feature engineering (source score, emotional language ratio, claim density)
- **Where**: Part of trust engine, not blocking pipeline
- **Tradeoff**: Binary classification is inherently reductive; always present with confidence + explainability

## 8.8 Contradiction Detection
- **Purpose**: Identify when two articles about the same event make opposing claims
- **Input**: Claim pairs from the same event
- **Output**: `{contradicts: bool, confidence: float, explanation: str}`
- **Model**: NLI (Natural Language Inference) model — `cross-encoder/nli-deberta-v3-base`
- **Where**: After claims are extracted and mapped to events
- **Tradeoff**: NLI models are compute-heavy; run on claim pairs selectively (only within same event)

## 8.9 Entity Linking
- **Purpose**: Resolve entity mentions to canonical knowledge graph nodes
- **Input**: NER output `[{entity_text, entity_type}]`
- **Output**: `entity_id` linking to `Entity` table
- **Model**: Fuzzy matching + pre-built alias table. For production, use `spaCy Entity Linker` with Wikidata
- **Tradeoff**: Full Wikidata linking is slow; start with alias-table approach

## Pipeline Orchestration

```python
async def process_article(raw: RawArticle) -> ProcessedArticle:
    clean = preprocessor.clean(raw.raw_text)
    embedding = embedder.encode(clean.text)
    entities = ner.extract(clean.text)
    sentiment = sentiment_analyzer.analyze(clean.text)
    locations = geo_extractor.extract(entities)
    summary = summarizer.summarize(clean.text)
    
    return ProcessedArticle(
        clean_text=clean.text,
        embedding_vector=embedding,
        entities_extracted=entities,
        sentiment_score=sentiment.compound,
        locations=locations,
        summary=summary,
        language=clean.language,
        word_count=clean.word_count,
    )
```

---

# 9. Event Detection Engine (Core)

## Detection Approaches

### Approach 1: Keyword Spike Detection
- Track keyword frequency in sliding window (1h, 6h, 24h)
- If a keyword's frequency exceeds 3x its rolling average → potential new event
- **Pro**: Fast, interpretable, low resource
- **Con**: Misses novel events with no keyword precedent

### Approach 2: Embedding-Based Clustering
- Every processed article gets an embedding
- Run incremental clustering: compare new embedding against existing event centroids
- If cosine similarity > 0.78 → assign to that event
- If no event matches → create new event
- **Pro**: Catches semantically related articles even with different keywords
- **Con**: Requires continuous centroid updates, cold start problem

### Approach 3: Hybrid (Recommended)
- First pass: keyword spike detection for fast alerting
- Second pass: embedding clustering for accurate assignment
- Reconciliation: merge keyword-detected events with embedding-detected events

## Event Creation Flow

```
New Article (with embedding)
    │
    ├──→ Compare against ALL active event centroids
    │        │
    │        ├── Match found (cosine > 0.78, time < 72h)
    │        │       → Assign to event
    │        │       → Recalculate centroid
    │        │       → Update event metadata
    │        │
    │        └── No match
    │                → Create new Event
    │                → Set status = EMERGING
    │                → Set centroid = article embedding
    │
    └──→ Check for merge candidates
             → If two events have centroid similarity > 0.85
             → AND share 3+ entities
             → Merge: smaller event absorbed into larger
```

## Merge Logic
1. Recalculate centroid as weighted average
2. Reassign all articles from old event to new
3. Merge timelines
4. Set `merged_into_id` on the absorbed event
5. Recalculate trust scores

## Split Logic
1. Run intra-event clustering periodically
2. If K-means with K=2 produces two clusters with silhouette > 0.6
3. AND each cluster has 3+ articles
4. Split: create child event with `parent_event_id`
5. Reassign articles to child events

---

# 10. Trust / Credibility System

## Source Scoring (0.0 - 1.0)

Factors:
- **Historical accuracy** (0.3 weight): Track how often claims from this source are later verified
- **Professional standards** (0.2): Has corrections policy, editorial board, authorship attribution
- **Bias consistency** (0.15): Consistent bias is penalized less than extreme swings
- **MBFC/IFCN rating** (0.2): Import from Media Bias/Fact Check database
- **Domain age & authority** (0.15): Heuristic — established outlets score higher

## Article Scoring (0.0 - 1.0)

```
article_trust = (
    0.30 * source_reliability_score +
    0.20 * language_quality_score +     # Low sensationalism, proper attribution
    0.20 * claim_verification_score +   # Claims cross-checked against other sources
    0.15 * consistency_score +          # Consistent with event consensus
    0.15 * authorship_score             # Named author, not "staff reporter"
)
```

## Cross-Source Validation
- For each event, collect all claims
- Group matching claims (same subject + predicate)
- Count supporting vs contradicting sources
- If >70% sources agree → claim marked VERIFIED
- If <30% → claim marked DISPUTED

## Contradiction Detection Pipeline
1. Extract claims from each article in an event
2. For each claim pair, run NLI model
3. If NLI says CONTRADICTION with confidence > 0.8 → flag
4. Generate explanation: "Source A says X, but Source B says Y"

## Explainability
Every trust score includes:
```json
{
    "score": 0.72,
    "breakdown": {
        "source_reliability": {"value": 0.85, "reason": "BBC: high MBFC rating"},
        "language_quality": {"value": 0.70, "reason": "Some emotional language detected"},
        "claim_verification": {"value": 0.65, "reason": "2 of 3 claims verified cross-source"},
        "consistency": {"value": 0.60, "reason": "Minor divergence from event consensus"}
    }
}
```

---

# 11. Search System

## Keyword Search
- PostgreSQL `tsvector` + `tsquery` for full-text search
- GIN index on `clean_text` and `title` columns
- Supports prefix matching, phrase search, boolean operators
- MVP approach — no external search engine needed initially

## Semantic Search
- Encode user query using same Sentence-BERT model
- Query vector DB for nearest neighbors
- Return articles + events ranked by cosine similarity
- Supports natural language questions: "What's happening with the Gaza ceasefire?"

## Event Search
- Search at the event level, not article level
- Match against event title, summary, and entity names
- Deduplicate: show events, not 50 articles about the same thing

## Trust-Aware Ranking

```
final_rank = (
    0.5 * relevance_score +      # Keyword or semantic match
    0.25 * trust_score +          # Event/article credibility
    0.15 * recency_score +        # Time decay
    0.10 * significance_score     # Event importance
)
```

## Technology

**MVP**: PostgreSQL full-text search + in-process vector similarity (numpy cosine)
**Production**: Elasticsearch/OpenSearch for text search + Qdrant/Milvus for vector search

---

# 12. Database Design

## PostgreSQL (Primary Relational Store)
Stores: Sources, RawArticles, ProcessedArticles, Events, Claims, Timelines, Alerts, Entities, EntityMentions, SourceCredibility
**Why**: ACID transactions, complex joins (event → articles → claims), proven at scale

## Redis (Cache + Streams)
Stores:
- Cached trending events, hot queries
- Session data
- Stream topics (raw_articles, processed, event_updates, alerts)
- Rate limit counters for ingestion
**Why**: Sub-millisecond reads, native streams support, atomic operations

## Vector Storage (Embeddings)
Stores: Article embeddings (768-dim), event centroid embeddings
**Options**:
- **MVP**: PostgreSQL `pgvector` extension — keeps everything in one DB
- **Scale**: Qdrant or Milvus for billion-scale vector search
**Why**: Cosine similarity search for semantic matching and clustering

## Elasticsearch (Optional, Production)
Stores: Searchable index of articles and events
**Why**: Superior full-text search with analyzers, fuzzy matching, aggregations
**MVP**: Skip — PostgreSQL tsvector is sufficient

---

# 13. Caching Strategy

## What to Cache
| Key Pattern | Data | TTL | Invalidation |
|---|---|---|---|
| `trending:global` | Top 20 events by velocity | 60s | Time-based |
| `event:{id}` | Full event with articles | 30s | On event update |
| `event:{id}:timeline` | Timeline entries | 60s | On new entry |
| `search:{query_hash}` | Search results | 120s | Time-based |
| `source:{domain}:score` | Source credibility | 1h | On score recalc |
| `stats:global` | System statistics | 30s | Time-based |

## Cache-Aside Pattern
1. Check Redis first
2. On miss → query PostgreSQL → write to Redis with TTL
3. On event mutations → explicitly invalidate relevant keys

## Write-Through for Hot Data
- Event significance scores written to both PostgreSQL and Redis simultaneously
- Trending computation reads from Redis only

---

# 14. API Design

## Core Endpoints

```
GET  /api/v1/events                    # List events (paginated, filterable)
GET  /api/v1/events/{id}               # Full event detail + articles + timeline
GET  /api/v1/events/{id}/articles      # Articles belonging to event
GET  /api/v1/events/{id}/timeline      # Event timeline
GET  /api/v1/events/{id}/claims        # Claims with verdicts
GET  /api/v1/events/{id}/trust         # Trust analysis with explainability

GET  /api/v1/search?q=...&type=...     # Unified search (keyword + semantic)
GET  /api/v1/trending                  # Trending events by velocity
GET  /api/v1/trending/topics           # Hot topics/categories

POST /api/v1/analyze                   # Submit text/URL for on-demand analysis
GET  /api/v1/analyze/{id}/status       # Check analysis status

GET  /api/v1/sources                   # List sources with credibility
GET  /api/v1/sources/{domain}/score    # Source credibility detail

GET  /api/v1/alerts                    # Active alerts
POST /api/v1/alerts/subscribe          # Subscribe to alert types

GET  /api/v1/entities/{id}             # Entity detail + related events
GET  /api/v1/entities/{id}/graph       # Knowledge graph neighbors

WS   /api/v1/stream/live               # WebSocket: real-time event updates
```

## Query Parameters (Events)
```
?status=DEVELOPING&category=POLITICS&min_trust=0.5&sort=-significance&page=1&limit=20
```

## Response Format
```json
{
    "data": [...],
    "meta": {
        "total": 145,
        "page": 1,
        "limit": 20,
        "processing_time_ms": 42
    }
}
```

---

# 15. Scalability

## Horizontal Scaling
- **Ingestion workers**: Scale independently per source type. RSS worker, API worker, scraper worker
- **NLP workers**: Most compute-heavy. Scale with GPU. Run behind a task queue
- **API servers**: Stateless FastAPI behind load balancer. Add instances as needed
- **Event detection**: Can be sharded by topic category

## Bottleneck Analysis
| Component | Bottleneck | Mitigation |
|---|---|---|
| NLP Pipeline | GPU memory & inference time | Batch processing, model quantization, worker scaling |
| Event Clustering | O(n) centroid comparisons | Pre-filter by category, approximate nearest neighbor |
| Database | Write throughput at scale | Connection pooling, read replicas, partitioning |
| Vector Search | Dimensionality at scale | Quantization, HNSW indexing, dedicated vector DB |

## Model Serving Separation
- NLP models served via separate process (`torch.serve` or `triton`)
- API layer calls model server over gRPC/HTTP
- Enables independent GPU scaling without affecting API availability

---

# 16. Reliability

- **Retries**: All external calls (APIs, scrapers) have 3-retry with exponential backoff
- **Idempotency**: Article UUID generated from content hash — reprocessing produces same result
- **Dead letter queue**: Failed messages moved to DLQ for manual inspection
- **Graceful degradation**: If NLP pipeline fails, article stored as `PENDING` and reprocessed later. API continues serving cached/existing data
- **Reprocessing**: Admin endpoint to re-run NLP pipeline on specific articles or date ranges
- **Health checks**: Each service exposes `/health` — orchestrator restarts unhealthy services

---

# 17. Monitoring

## Key Metrics
| Metric | Source | Alert Threshold |
|---|---|---|
| Ingestion rate (articles/min) | Ingestion workers | < 5 for 10 min = alert |
| Queue depth | Redis Streams | > 10,000 pending = alert |
| NLP latency (p95) | NLP Worker | > 5s per article = alert |
| API latency (p95) | FastAPI | > 500ms = alert |
| Event detection rate | Event engine | < 1 new event/hour = investigate |
| Error rate | All services | > 1% = alert |
| Model inference time | NLP Worker | Track per-model for optimization |

## Stack
- **Metrics**: Prometheus + Grafana
- **Logging**: Structured JSON logs → stdout → collected by log aggregator
- **Tracing**: OpenTelemetry for request tracing across services

---

# 18. Security & Ethics

## Misinformation Risks
TruthLens scores reliability but does NOT claim absolute truth. All labels are:
- Probabilistic (confidence scores, not binary)
- Explainable (reasons provided)
- Transparent (methodology documented)

## Safe Labeling
- Never label an article as "FAKE NEWS" — use "LOW CREDIBILITY (confidence: 0.73)"
- Always show the reasoning breakdown
- Flag but don't suppress — filtering is the consumer's choice

## API Security
- JWT-based authentication (future)
- Rate limiting per API key (10 req/s default)
- Input sanitization on all endpoints
- No PII stored — articles are public information

## Ethical Considerations
- Bias in training data → regularly audit model outputs
- Source credibility scores → transparent methodology, appeal process
- Avoid encoding political bias into system design

---

# 19. MVP vs Advanced

## MVP (Phase 1-2, ~4 weeks)
- RSS ingestion (5-10 sources)
- Text preprocessing + embedding generation
- Basic event detection (cosine similarity clustering)
- Source credibility scoring (static + MBFC data)
- PostgreSQL storage with pgvector
- REST API: events, search, trending
- Redis caching
- Docker Compose deployment

## Growth (Phase 3-4, ~4 weeks)
- Full NLP pipeline (NER, sentiment, summarization)
- Fake news classification
- Contradiction detection
- Knowledge graph (entity linking)
- Alert system
- Event timelines
- Semantic search

## Advanced (Phase 5+, ongoing)
- Multimodal analysis (images, deepfakes)
- Propaganda detection
- GDELT integration
- Kafka migration (if scale demands)
- Real-time WebSocket streaming
- Model serving separation (Triton)
- Elasticsearch integration
- Geographic heat maps

---

# 20. Tech Stack

| Layer | Technology | Why |
|---|---|---|
| API Framework | **FastAPI** | Async, auto-docs, Pydantic validation, type safety |
| Task Queue | **Celery + Redis** | Proven, Python-native, easy worker scaling |
| Streaming | **Redis Streams** | Already using Redis, Kafka-like semantics, lower ops |
| Primary DB | **PostgreSQL + pgvector** | ACID, joins, full-text, vector search in one DB |
| Cache | **Redis** | Sub-ms reads, native data structures, streams |
| Vector DB (scale) | **Qdrant** | Purpose-built ANN search, easy migration from pgvector |
| Search (scale) | **Elasticsearch** | Best-in-class full-text search with analyzers |
| NLP Models | **sentence-transformers, spaCy, HuggingFace** | State-of-art, open-source, Python-native |
| NER | **spaCy** | Fast, accurate, pre-trained pipelines |
| Graph DB (optional) | **Neo4j** | Entity relationships, already in docker-compose |
| Migrations | **Alembic** | SQLAlchemy-native, version-controlled schema changes |
| HTTP Client | **httpx** | Async HTTP, connection pooling |
| Testing | **pytest + httpx.AsyncClient** | Async test support for FastAPI |
| Containerization | **Docker + docker-compose** | Reproducible environments |

---

# 21. Service / Folder Architecture

```
truthlens/
├── src/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application factory
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py            # Pydantic Settings (env-based config)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                # SQLAlchemy Base
│   │   ├── source.py              # Source model
│   │   ├── article.py             # RawArticle, ProcessedArticle
│   │   ├── event.py               # Event, EventArticle
│   │   ├── claim.py               # Claim
│   │   ├── entity.py              # Entity, EntityMention
│   │   ├── timeline.py            # TimelineEntry
│   │   └── alert.py               # Alert
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── article.py
│   │   ├── event.py
│   │   ├── search.py
│   │   └── trust.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py                # Dependency injection (DB sessions, etc.)
│   │   ├── events.py
│   │   ├── search.py
│   │   ├── trending.py
│   │   ├── analyze.py
│   │   ├── trust.py
│   │   ├── alerts.py
│   │   ├── sources.py
│   │   └── websocket.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── base.py                # BaseConnector ABC
│   │   ├── rss.py
│   │   ├── newsapi.py
│   │   ├── scraper.py
│   │   └── scheduler.py
│   ├── streaming/
│   │   ├── __init__.py
│   │   ├── producer.py
│   │   ├── consumer.py
│   │   └── topics.py
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── pipeline.py            # Orchestrator
│   │   ├── preprocessor.py
│   │   ├── embeddings.py
│   │   ├── ner.py
│   │   ├── sentiment.py
│   │   ├── summarizer.py
│   │   ├── geo_extractor.py
│   │   └── fake_news.py
│   ├── events/
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   ├── clusterer.py
│   │   ├── merger.py
│   │   └── timeline.py
│   ├── trust/
│   │   ├── __init__.py
│   │   ├── source_scorer.py
│   │   ├── article_scorer.py
│   │   ├── contradiction.py
│   │   └── explainer.py
│   ├── search/
│   │   ├── __init__.py
│   │   ├── keyword.py
│   │   ├── semantic.py
│   │   └── ranker.py
│   ├── alerts/
│   │   ├── __init__.py
│   │   └── engine.py
│   ├── knowledge/
│   │   ├── __init__.py
│   │   └── entity_linker.py
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── ingestion_worker.py
│   │   ├── nlp_worker.py
│   │   └── event_worker.py
│   └── utils/
│       ├── __init__.py
│       ├── hashing.py
│       └── time_utils.py
├── migrations/
│   └── alembic/
├── tests/
├── infra/
│   ├── docker-compose.yml
│   └── Dockerfile
├── requirements.txt
├── alembic.ini
├── .env.example
├── .gitignore
└── README.md
```

---

# 22. Deployment

## Docker Services

```yaml
services:
  api:          # FastAPI (uvicorn, 2+ replicas)
  nlp-worker:   # Celery worker (GPU-capable)
  event-worker: # Event detection worker
  ingest-worker: # Ingestion scheduler
  postgres:     # PostgreSQL 15 + pgvector
  redis:        # Redis 7 (cache + streams + Celery broker)
  neo4j:        # Neo4j 5 (optional, knowledge graph)
```

## Cloud Approach
- **Dev**: Docker Compose on local machine
- **Staging**: Single VM (AWS EC2 / GCP Compute) running docker-compose
- **Production**: Kubernetes with separate deployments per service
  - API: 2+ pods, horizontal pod autoscaler
  - NLP Worker: GPU node pool, scale on queue depth
  - Managed PostgreSQL (RDS/Cloud SQL)
  - Managed Redis (ElastiCache/Memorystore)

---

# 23. Interview Value

## One-Line Description
> **"Built a real-time news intelligence platform that ingests articles from 50+ sources, uses NLP to detect and cluster emerging events, scores credibility across sources, and serves enriched intelligence through a trust-aware search API — processing 10K+ articles/hour through a streaming pipeline."**

## Why This Project Is Impressive

1. **Systems Design Depth**: Streaming pipelines, event-driven architecture, polyglot persistence, caching strategies — this is not a CRUD app
2. **AI/ML Integration**: Production NLP pipeline with embeddings, NER, sentiment, clustering, and fake news detection running on real data
3. **Novel Abstraction**: Event-centric modeling is a non-trivial design choice that enables features impossible with article-centric approaches
4. **Scale Thinking**: Designed from day one for horizontal scaling, async processing, and graceful degradation
5. **Trust Engineering**: Credibility scoring with explainability demonstrates understanding of responsible AI
6. **Full Pipeline**: Raw data → structured intelligence → searchable API — covers the entire data engineering lifecycle
