"""Alerts API Router — alert management endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.models.database import get_db
from src.models.alert import Alert
from src.schemas.schemas import AlertResponse

router = APIRouter()


@router.get("")
def list_alerts(
    severity: str = Query(None, description="Filter by severity: LOW, MEDIUM, HIGH, CRITICAL"),
    acknowledged: bool = Query(None, description="Filter by acknowledgment status"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List active alerts."""
    query = db.query(Alert).order_by(Alert.triggered_at.desc())

    if severity:
        query = query.filter(Alert.severity == severity)
    if acknowledged is not None:
        query = query.filter(Alert.acknowledged == acknowledged)

    alerts = query.limit(limit).all()

    return {
        "data": [AlertResponse.model_validate(a) for a in alerts],
        "meta": {"count": len(alerts)},
    }


@router.post("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str, db: Session = Depends(get_db)):
    """Acknowledge an alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged = True
    db.commit()
    return {"status": "acknowledged", "alert_id": alert_id}
