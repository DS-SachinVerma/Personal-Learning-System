"""Shared helpers: db session, slugify, and the changelog writer."""
import re
from sqlalchemy.orm import Session
from .database import SessionLocal
from . import models


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def slugify(text: str) -> str:
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-") or "item"


def unique_slug(db: Session, model, base: str, exclude_id: int | None = None) -> str:
    """Return a slug not already taken by another row of `model`."""
    slug = slugify(base)
    candidate = slug
    n = 2
    while True:
        q = db.query(model).filter(model.slug == candidate)
        if exclude_id is not None:
            q = q.filter(model.id != exclude_id)
        if q.first() is None:
            return candidate
        candidate = f"{slug}-{n}"
        n += 1


def log_change(db: Session, entity_type: str, entity_id: int, entity_name: str,
               kind: str, note: str = "") -> None:
    """Record one activity-feed row. The daily digest reads these."""
    db.add(models.ChangeLog(
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        kind=kind,
        note=note,
    ))
