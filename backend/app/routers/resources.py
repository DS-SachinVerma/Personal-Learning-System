from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from ..deps import get_db, log_change
from .. import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Resource])
def list_resources(
    status: Optional[str] = None,
    type: Optional[str] = None,
    source: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Resource)
    if status:
        query = query.filter(models.Resource.status == status)
    if type:
        query = query.filter(models.Resource.type == type)
    if source:
        query = query.filter(models.Resource.source == source)
    if q:
        like = f"%{q}%"
        query = query.filter(models.Resource.title.ilike(like) | models.Resource.summary.ilike(like))
    return query.order_by(models.Resource.created_at.desc()).all()


@router.get("/{resource_id}", response_model=schemas.Resource)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    r = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return r


@router.post("/", response_model=schemas.Resource)
def create_resource(payload: schemas.ResourceCreate, db: Session = Depends(get_db)):
    """Create — or upsert. If (source, external_id) already exists, we refresh
    the live bits (stars, last_seen) instead of inserting a duplicate."""
    existing = None
    if payload.external_id and payload.source:
        existing = (
            db.query(models.Resource)
            .filter(models.Resource.source == payload.source,
                    models.Resource.external_id == payload.external_id)
            .first()
        )
    if existing:
        existing.last_seen_at = datetime.utcnow()
        if payload.stars is not None:
            existing.stars = payload.stars
        db.commit()
        db.refresh(existing)
        return existing

    r = models.Resource(**payload.dict())
    db.add(r)
    db.flush()
    log_change(db, "resource", r.id, r.title, "added", f"New {r.type or 'source'} from {r.source or 'manual'}")
    db.commit()
    db.refresh(r)
    return r


@router.put("/{resource_id}", response_model=schemas.Resource)
def update_resource(resource_id: int, payload: schemas.ResourceUpdate, db: Session = Depends(get_db)):
    r = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(r, k, v)
    log_change(db, "resource", r.id, r.title, "updated", "Resource edited")
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{resource_id}")
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    r = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    db.delete(r)
    db.commit()
    return {"message": "Resource deleted"}


# ------------------------- version history -------------------------

@router.post("/{resource_id}/versions", response_model=schemas.ResourceVersion)
def add_version(resource_id: int, payload: schemas.ResourceVersionCreate, db: Session = Depends(get_db)):
    r = db.query(models.Resource).filter(models.Resource.id == resource_id).first()
    if r is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    v = models.ResourceVersion(
        resource_id=resource_id,
        version_label=payload.version_label,
        changed_on=payload.changed_on or datetime.utcnow(),
        what_changed=payload.what_changed,
        why_it_matters=payload.why_it_matters,
        link=payload.link,
    )
    db.add(v)
    r.updated_at = datetime.utcnow()
    db.flush()
    log_change(db, "resource", r.id, r.title, "version",
               f"{payload.version_label or 'update'}: {payload.what_changed or ''}".strip())
    db.commit()
    db.refresh(v)
    return v


@router.delete("/{resource_id}/versions/{version_id}")
def delete_version(resource_id: int, version_id: int, db: Session = Depends(get_db)):
    v = (
        db.query(models.ResourceVersion)
        .filter(models.ResourceVersion.id == version_id,
                models.ResourceVersion.resource_id == resource_id)
        .first()
    )
    if v is None:
        raise HTTPException(status_code=404, detail="Version not found")
    db.delete(v)
    db.commit()
    return {"message": "Version deleted"}
