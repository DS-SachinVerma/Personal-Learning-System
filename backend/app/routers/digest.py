from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from ..deps import get_db
from .. import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.ChangeLogEntry])
def get_digest(
    days: int = 1,
    since: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """The 'what did we add/change' feed.

    Default (days=1) is today's activity — the daily digest. Pass days=7 for a
    week, or an ISO `since` timestamp for a custom window.
    """
    if since:
        cutoff = datetime.fromisoformat(since)
    else:
        cutoff = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(models.ChangeLog)
        .filter(models.ChangeLog.created_at >= cutoff)
        .order_by(models.ChangeLog.created_at.desc())
        .all()
    )
