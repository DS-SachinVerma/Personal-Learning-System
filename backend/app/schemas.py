"""Pydantic schemas for the technique-library API.

Read models expose the relationships (a task carries its techniques and the
insights our sources give for it) so a single GET renders a whole page. Write
models take plain id lists / ids for the links.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ---- lightweight "chip" views, used when nested inside a parent ----

class TaskChip(BaseModel):
    id: int
    name: str
    slug: Optional[str] = None
    domain: Optional[str] = None

    class Config:
        from_attributes = True


class TechniqueChip(BaseModel):
    id: int
    name: str
    slug: Optional[str] = None
    maturity: Optional[str] = None

    class Config:
        from_attributes = True


class ResourceChip(BaseModel):
    id: int
    title: str
    type: Optional[str] = None
    link: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    stars: Optional[int] = None

    class Config:
        from_attributes = True


# ---------------------------------- Insight ---------------------------------
# The takeaway a resource gives for a task/technique — and the link itself.

class InsightBase(BaseModel):
    title: Optional[str] = None
    detail: Optional[str] = None
    kind: str = "use"          # 'use' (actionable) | 'study' (background)
    task_id: Optional[int] = None
    technique_id: Optional[int] = None


class InsightCreate(InsightBase):
    resource_id: int


class InsightUpdate(InsightBase):
    pass


class Insight(BaseModel):
    id: int
    title: Optional[str] = None
    detail: Optional[str] = None
    kind: str = "use"
    created_at: datetime
    resource: Optional[ResourceChip] = None
    task: Optional[TaskChip] = None
    technique: Optional[TechniqueChip] = None

    class Config:
        from_attributes = True


# ------------------------- Resource version history -------------------------

class ResourceVersionBase(BaseModel):
    version_label: Optional[str] = None
    changed_on: Optional[datetime] = None
    what_changed: Optional[str] = None
    why_it_matters: Optional[str] = None
    link: Optional[str] = None


class ResourceVersionCreate(ResourceVersionBase):
    pass


class ResourceVersion(ResourceVersionBase):
    id: int
    resource_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------- Resource --------------------------------

class ResourceBase(BaseModel):
    title: str
    type: Optional[str] = None
    link: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[str] = None
    status: str = "intake"
    source: Optional[str] = None
    external_id: Optional[str] = None
    author: Optional[str] = None
    stars: Optional[int] = None
    raw: Optional[str] = None
    published_at: Optional[datetime] = None


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    link: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[str] = None
    status: Optional[str] = None
    author: Optional[str] = None
    stars: Optional[int] = None
    last_reviewed_at: Optional[datetime] = None


class Resource(ResourceBase):
    id: int
    last_seen_at: Optional[datetime] = None
    last_reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    insights: List[Insight] = []
    versions: List[ResourceVersion] = []

    class Config:
        from_attributes = True


# ---------------------------------- Technique -------------------------------

class TechniqueBase(BaseModel):
    name: str
    slug: Optional[str] = None
    summary: Optional[str] = None
    maturity: Optional[str] = None
    tags: Optional[str] = None


class TechniqueCreate(TechniqueBase):
    task_ids: List[int] = []


class TechniqueUpdate(BaseModel):
    name: Optional[str] = None
    summary: Optional[str] = None
    maturity: Optional[str] = None
    tags: Optional[str] = None
    last_reviewed_at: Optional[datetime] = None
    task_ids: Optional[List[int]] = None


class Technique(TechniqueBase):
    id: int
    last_reviewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    tasks: List[TaskChip] = []
    insights: List[Insight] = []

    class Config:
        from_attributes = True


# ---------------------------------- Experiment ------------------------------

class ExperimentBase(BaseModel):
    title: str
    task_id: int
    dataset: Optional[str] = None
    metric: Optional[str] = None
    results: Optional[str] = None
    code_link: Optional[str] = None


class ExperimentCreate(ExperimentBase):
    pass


class ExperimentUpdate(BaseModel):
    title: Optional[str] = None
    dataset: Optional[str] = None
    metric: Optional[str] = None
    results: Optional[str] = None
    code_link: Optional[str] = None


class Experiment(ExperimentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ------------------------------------- Task ---------------------------------

class TaskBase(BaseModel):
    name: str
    slug: Optional[str] = None
    domain: Optional[str] = None
    one_liner: Optional[str] = None
    overview: Optional[str] = None
    tags: Optional[str] = None


class TaskCreate(TaskBase):
    technique_ids: List[int] = []


class TaskUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    one_liner: Optional[str] = None
    overview: Optional[str] = None
    tags: Optional[str] = None
    technique_ids: Optional[List[int]] = None


class TaskSummary(TaskBase):
    """List view — no heavy nested payloads, just counts."""
    id: int
    technique_count: int = 0
    resource_count: int = 0
    experiment_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True


class Task(TaskBase):
    """Detail view — the full task page in one response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    techniques: List[TechniqueChip] = []
    insights: List[Insight] = []
    experiments: List[Experiment] = []

    class Config:
        from_attributes = True


# ---------------------------------- Digest ----------------------------------

class ChangeLogEntry(BaseModel):
    id: int
    entity_type: str
    entity_id: int
    entity_name: Optional[str] = None
    kind: str
    note: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
