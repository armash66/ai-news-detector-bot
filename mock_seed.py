import os
os.environ["USE_SQLITE"] = "True"

from datetime import datetime, timezone, timedelta
from models.database import SessionLocal, engine
from models.base import Base
from models import Event, EventArticle, Alert, TimelineEntry, EntityMention

def seed():
    # Ensure tables exist
    from models import Source, RawArticle, ProcessedArticle, Claim, Entity
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    
    # Check if already seeded
    if db.query(Event).count() > 0:
        print("Database already seeded.")
        return

    now = datetime.now(timezone.utc)

    # Event 1
    e1 = Event(
        id="evt_001",
        title="Global Supply Chain Disruptions Intensify Amid Strategic Port Closure in Southeast Asia",
        summary="Critical logistical hubs report a 40% decrease in container throughput as regional tensions lead to temporary suspension of operations. Analysts predict immediate impacts on consumer electronics pricing.",
        category="Geopolitics",
        status="BREAKING",
        significance_score=0.92,
        trust_score=0.95,
        article_count=32,
        source_count=14,
        first_seen_at=now - timedelta(minutes=14),
        last_updated_at=now - timedelta(minutes=2)
    )
    
    e1_t1 = TimelineEntry(id="tl_001", event_id="evt_001", timestamp=now - timedelta(hours=2), description="Port authority formally announces complete suspension of commercial throughput.", entry_type="UPDATE", significance=0.9)
    e1_t2 = TimelineEntry(id="tl_002", event_id="evt_001", timestamp=now - timedelta(hours=6), description="Initial widespread delays reported by major freight carriers.", entry_type="INITIAL", significance=0.7)
    
    a1 = Alert(
        id="alt_001",
        event_id="evt_001",
        alert_type="Logistics Risk",
        severity="CRITICAL",
        title="Semiconductor Export Restrictions: Tier 1 Regulatory Shift",
        description="New regulatory framework announced affecting 45% of current supply chain routes in Southeast Asia.",
        triggered_at=now - timedelta(minutes=12)
    )

    # Event 2
    e2 = Event(
        id="evt_002",
        title="Breakthrough in Solid-State Battery Tech Promises 1,000 Mile EV Range",
        summary="A major automotive conglomerate unveils prototype high-density cells that eliminate thermal runaway risks. Industry experts suggest mass production could begin by late 2026.",
        category="Tech & Markets",
        status="TRENDING",
        significance_score=0.88,
        trust_score=0.85,
        article_count=18,
        source_count=9,
        first_seen_at=now - timedelta(hours=2),
        last_updated_at=now - timedelta(minutes=15)
    )

    # Event 3
    e3 = Event(
        id="evt_003",
        title="Central European Power Grid Faces Critical Strain Due to Maintenance Overlap",
        summary="Scheduled maintenance in Germany and unexpected outages in France create a 2.4GW deficit, driving spot prices to 6-month highs. Secondary manufacturers slowing production.",
        category="Environment",
        status="DEVELOPING RISK",
        significance_score=0.75,
        trust_score=0.65,
        article_count=8,
        source_count=5,
        first_seen_at=now - timedelta(hours=3),
        last_updated_at=now - timedelta(hours=1)
    )
    
    a2 = Alert(
        id="alt_002",
        event_id="evt_003",
        alert_type="Energy Grid",
        severity="WARNING",
        title="Port Congestion Indices Hit 12-Month High",
        description="Significant delays reported at major logistics hubs. Global trade velocity dropped by 3.2% in the last 48 hours.",
        triggered_at=now - timedelta(hours=6)
    )

    db.add_all([e1, e2, e3, e1_t1, e1_t2, a1, a2])
    db.commit()
    print("Database seeded with mock intelligence successfully!")

if __name__ == "__main__":
    seed()
