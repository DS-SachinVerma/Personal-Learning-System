from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from ..deps import get_db, unique_slug, log_change
from .. import models, schemas

router = APIRouter()


def _resolve(db: Session, model, ids):
    if not ids:
        return []
    return db.query(model).filter(model.id.in_(ids)).all()


@router.get("/domains")
def list_domains(db: Session = Depends(get_db)):
    """Top-level browse: each domain with how many tasks sit under it."""
    rows = (
        db.query(models.Task.domain, func.count(models.Task.id))
        .group_by(models.Task.domain)
        .order_by(models.Task.domain)
        .all()
    )
    return [{"domain": d or "Uncategorized", "task_count": c} for d, c in rows]


@router.get("/", response_model=List[schemas.TaskSummary])
def list_tasks(
    domain: Optional[str] = None,
    tag: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Task)
    if domain:
        query = query.filter(models.Task.domain == domain)
    if tag:
        query = query.filter(models.Task.tags.contains(tag))
    if q:
        like = f"%{q}%"
        query = query.filter(models.Task.name.ilike(like) | models.Task.one_liner.ilike(like))
    tasks = query.order_by(models.Task.domain, models.Task.name).all()

    out = []
    for t in tasks:
        out.append(schemas.TaskSummary(
            id=t.id, name=t.name, slug=t.slug, domain=t.domain,
            one_liner=t.one_liner, overview=t.overview, tags=t.tags,
            created_at=t.created_at,
            technique_count=len(t.techniques),
            # distinct sources, since one resource can give several insights
            resource_count=len({i.resource_id for i in t.insights}),
            experiment_count=len(t.experiments),
        ))
    return out


def _get_task(db: Session, id_or_slug: str) -> models.Task:
    q = db.query(models.Task)
    task = q.filter(models.Task.slug == id_or_slug).first()
    if task is None and id_or_slug.isdigit():
        task = q.filter(models.Task.id == int(id_or_slug)).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/{id_or_slug}", response_model=schemas.Task)
def get_task(id_or_slug: str, db: Session = Depends(get_db)):
    return _get_task(db, id_or_slug)


@router.post("/", response_model=schemas.Task)
def create_task(payload: schemas.TaskCreate, db: Session = Depends(get_db)):
    slug = unique_slug(db, models.Task, payload.slug or payload.name)
    task = models.Task(
        name=payload.name, slug=slug, domain=payload.domain,
        one_liner=payload.one_liner, overview=payload.overview, tags=payload.tags,
    )
    task.techniques = _resolve(db, models.Technique, payload.technique_ids)
    db.add(task)
    db.flush()
    log_change(db, "task", task.id, task.name, "added", f"New task in {task.domain or 'Uncategorized'}")
    db.commit()
    db.refresh(task)
    return task


@router.put("/{task_id}", response_model=schemas.Task)
def update_task(task_id: int, payload: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    data = payload.dict(exclude_unset=True)
    data.pop("technique_ids", None)
    for k, v in data.items():
        setattr(task, k, v)
    if payload.technique_ids is not None:
        task.techniques = _resolve(db, models.Technique, payload.technique_ids)
    log_change(db, "task", task.id, task.name, "updated", "Task edited")
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted"}
