from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from ..deps import get_db, log_change
from .. import models, schemas

router = APIRouter()


@router.get("/", response_model=List[schemas.Experiment])
def list_experiments(task_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(models.Experiment)
    if task_id:
        query = query.filter(models.Experiment.task_id == task_id)
    return query.order_by(models.Experiment.created_at.desc()).all()


@router.get("/{experiment_id}", response_model=schemas.Experiment)
def get_experiment(experiment_id: int, db: Session = Depends(get_db)):
    e = db.query(models.Experiment).filter(models.Experiment.id == experiment_id).first()
    if e is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    return e


@router.post("/", response_model=schemas.Experiment)
def create_experiment(payload: schemas.ExperimentCreate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == payload.task_id).first()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    e = models.Experiment(**payload.dict())
    db.add(e)
    db.flush()
    log_change(db, "experiment", e.id, e.title, "added", f"Benchmark on task '{task.name}'")
    db.commit()
    db.refresh(e)
    return e


@router.put("/{experiment_id}", response_model=schemas.Experiment)
def update_experiment(experiment_id: int, payload: schemas.ExperimentUpdate, db: Session = Depends(get_db)):
    e = db.query(models.Experiment).filter(models.Experiment.id == experiment_id).first()
    if e is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    for k, v in payload.dict(exclude_unset=True).items():
        setattr(e, k, v)
    db.commit()
    db.refresh(e)
    return e


@router.delete("/{experiment_id}")
def delete_experiment(experiment_id: int, db: Session = Depends(get_db)):
    e = db.query(models.Experiment).filter(models.Experiment.id == experiment_id).first()
    if e is None:
        raise HTTPException(status_code=404, detail="Experiment not found")
    db.delete(e)
    db.commit()
    return {"message": "Experiment deleted"}
