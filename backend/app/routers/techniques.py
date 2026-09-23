from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional
from datetime import datetime

from ..deps import get_db, unique_slug, log_change
from .. import models, schemas

router = APIRouter()

_TECH_EAGER = (
    selectinload(models.Technique.tasks),
    selectinload(models.Technique.insights).selectinload(models.Insight.resource),
    selectinload(models.Technique.insights).selectinload(models.Insight.task),
    selectinload(models.Technique.insights).selectinload(models.Insight.technique),
)


def _resolve(db: Session, model, ids):
    if not ids:
        return []
    return db.query(model).filter(model.id.in_(ids)).all()


@router.get("/", response_model=List[schemas.Technique])
def list_techniques(
    task_id: Optional[int] = None,
    tag: Optional[str] = None,
    maturity: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Technique).options(*_TECH_EAGER)
    if task_id:
        query = query.join(models.Technique.tasks).filter(models.Task.id == task_id)
    if tag:
        query = query.filter(models.Technique.tags.contains(tag))
    if maturity:
        query = query.filter(models.Technique.maturity == maturity)
    if q:
        like = f"%{q}%"
        query = query.filter(models.Technique.name.ilike(like) | models.Technique.summary.ilike(like))
    return query.order_by(models.Technique.name).all()


@router.get("/{technique_id}", response_model=schemas.Technique)
def get_technique(technique_id: int, db: Session = Depends(get_db)):
    tech = (
        db.query(models.Technique).options(*_TECH_EAGER)
        .filter(models.Technique.id == technique_id).first()
    )
    if tech is None:
        raise HTTPException(status_code=404, detail="Technique not found")
    return tech


@router.post("/", response_model=schemas.Technique)
def create_technique(payload: schemas.TechniqueCreate, db: Session = Depends(get_db)):
    # Concept dedup: if a technique with this slug already exists, link to it
    # instead of creating a twin.
    slug_base = payload.slug or payload.name
    from ..deps import slugify
    existing = db.query(models.Technique).filter(models.Technique.slug == slugify(slug_base)).first()
    if existing:
        if payload.task_ids:
            existing.tasks = list({*existing.tasks, *_resolve(db, models.Task, payload.task_ids)})
        log_change(db, "technique", existing.id, existing.name, "linked", "Merged into existing technique")
        db.commit()
        db.refresh(existing)
        return existing

    tech = models.Technique(
        name=payload.name, slug=unique_slug(db, models.Technique, slug_base),
        summary=payload.summary, maturity=payload.maturity, tags=payload.tags,
    )
    tech.tasks = _resolve(db, models.Task, payload.task_ids)
    db.add(tech)
    db.flush()
    log_change(db, "technique", tech.id, tech.name, "added", "New technique")
    db.commit()
    db.refresh(tech)
    return tech


@router.put("/{technique_id}", response_model=schemas.Technique)
def update_technique(technique_id: int, payload: schemas.TechniqueUpdate, db: Session = Depends(get_db)):
    tech = db.query(models.Technique).filter(models.Technique.id == technique_id).first()
    if tech is None:
        raise HTTPException(status_code=404, detail="Technique not found")
    data = payload.dict(exclude_unset=True)
    data.pop("task_ids", None)
    for k, v in data.items():
        setattr(tech, k, v)
    if payload.task_ids is not None:
        tech.tasks = _resolve(db, models.Task, payload.task_ids)
    log_change(db, "technique", tech.id, tech.name, "updated", "Technique edited")
    db.commit()
    db.refresh(tech)
    return tech


@router.delete("/{technique_id}")
def delete_technique(technique_id: int, db: Session = Depends(get_db)):
    tech = db.query(models.Technique).filter(models.Technique.id == technique_id).first()
    if tech is None:
        raise HTTPException(status_code=404, detail="Technique not found")
    db.delete(tech)
    db.commit()
    return {"message": "Technique deleted"}
