from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..deps import get_db, log_change
from .. import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Insight])
def list_insights(
    resource_id: Optional[int] = None,
    task_id: Optional[int] = None,
    technique_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Insight)
    if resource_id:
        query = query.filter(models.Insight.resource_id == resource_id)
    if task_id:
        query = query.filter(models.Insight.task_id == task_id)
    if technique_id:
        query = query.filter(models.Insight.technique_id == technique_id)
    return query.order_by(models.Insight.created_at.desc()).all()


@router.post("/", response_model=schemas.Insight)
def create_insight(payload: schemas.InsightCreate, db: Session = Depends(get_db)):
    resource = db.query(models.Resource).filter(models.Resource.id == payload.resource_id).first()
    if resource is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    if payload.task_id is None and payload.technique_id is None:
        raise HTTPException(status_code=400, detail="An insight must point to a task and/or a technique")
    if payload.task_id and not db.query(models.Task).get(payload.task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    if payload.technique_id and not db.query(models.Technique).get(payload.technique_id):
        raise HTTPException(status_code=404, detail="Technique not found")

    ins = models.Insight(
        resource_id=payload.resource_id,
        task_id=payload.task_id,
        technique_id=payload.technique_id,
        title=payload.title,
        detail=payload.detail,
        kind=payload.kind or "use",
    )
    db.add(ins)
    # curating an insight counts as reviewing the source
    if resource.status == "intake":
        resource.status = "reviewed"
    from datetime import datetime
    resource.last_reviewed_at = datetime.utcnow()
    db.flush()
    target = ins.task.name if ins.task else (ins.technique.name if ins.technique else "?")
    log_change(db, "insight", ins.id, payload.title or resource.title, "insight",
               f"'{resource.title}' → {target}: {payload.title or ''}".strip())
    db.commit()
    db.refresh(ins)
    return ins


@router.put("/{insight_id}", response_model=schemas.Insight)
def update_insight(insight_id: int, payload: schemas.InsightUpdate, db: Session = Depends(get_db)):
    ins = db.query(models.Insight).filter(models.Insight.id == insight_id).first()
    if ins is None:
        raise HTTPException(status_code=404, detail="Insight not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(ins, k, v)
    db.commit()
    db.refresh(ins)
    return ins


@router.delete("/{insight_id}")
def delete_insight(insight_id: int, db: Session = Depends(get_db)):
    ins = db.query(models.Insight).filter(models.Insight.id == insight_id).first()
    if ins is None:
        raise HTTPException(status_code=404, detail="Insight not found")
    db.delete(ins)
    db.commit()
    return {"message": "Insight deleted"}
