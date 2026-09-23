from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Table, UniqueConstraint, Index,
)
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

# ---------------------------------------------------------------------------
# task_technique is the only plain many-to-many: which techniques are candidate
# approaches for a task. (One "embeddings" technique can be a candidate for
# both "Semantic Search" and "Clustering" without being duplicated.)
#
# The resource <-> task/technique connection is NOT a plain link — it's the
# Insight model below, because one source (esp. a blog) contributes a DIFFERENT
# takeaway to each task it touches.
# ---------------------------------------------------------------------------

task_technique = Table(
    "task_technique",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("technique_id", Integer, ForeignKey("techniques.id", ondelete="CASCADE"), primary_key=True),
)


class Task(Base):
    """A *kind of job* you can be assigned (e.g. 'Text Classification').

    The hub of the library. Open a task and you see its candidate techniques,
    the insights our sources give for doing it, and any benchmarks. Replaces
    the old to-do-item meaning of 'Task'.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)              # "Time-Series Forecasting"
    slug = Column(String, unique=True, index=True)  # "time-series-forecasting" — concept-dedup key
    domain = Column(String, index=True)             # top-level bucket, e.g. "Time Series"
    one_liner = Column(String)                       # when to reach for this task
    overview = Column(Text)                          # markdown: framing, inputs/outputs, pitfalls
    tags = Column(String)                            # comma-separated, free cross-cutting axis
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    techniques = relationship("Technique", secondary=task_technique, back_populates="tasks")
    insights = relationship("Insight", back_populates="task")
    experiments = relationship("Experiment", back_populates="task", cascade="all, delete-orphan")


class Technique(Base):
    """A method/approach for doing one or more tasks (e.g. 'XGBoost')."""
    __tablename__ = "techniques"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    slug = Column(String, unique=True, index=True)   # concept-dedup key: one 'embeddings', many sources
    summary = Column(Text)          # markdown: what it is, when to use, pros/cons, gotchas
    maturity = Column(String)       # experimental | emerging | proven | legacy
    tags = Column(String)

    last_reviewed_at = Column(DateTime, default=datetime.utcnow)   # drives the "needs refresh" badge

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tasks = relationship("Task", secondary=task_technique, back_populates="techniques")
    insights = relationship("Insight", back_populates="technique")


class Resource(Base):
    """A concrete source: a GitHub repo, a paper, a **blog**, docs, or a video.

    Freshly collected items land here with status='intake'. The ingestion
    script only fills the raw fields; curation (writing insights + linking)
    happens afterwards and flips status to 'reviewed'.

    Exact-duplicate protection: (source, external_id) is unique, so the same
    arXiv id, owner/repo, or blog URL can never be inserted twice — the script
    upserts. How it changes over time lives in its `versions` list.

    What it *teaches us*, per task, lives in its `insights` list — one resource
    can hold several insights aimed at different tasks.
    """
    __tablename__ = "resources"
    __table_args__ = (
        UniqueConstraint("source", "external_id", name="uq_resource_source_external"),
    )

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    type = Column(String)           # paper | repo | blog | video | docs | course | book
    link = Column(String)
    summary = Column(Text)          # markdown: what it is overall (the per-task detail is in insights)
    tags = Column(String)

    # Triage / intake workflow
    status = Column(String, default="intake")   # intake | reviewed | archived
    source = Column(String)                       # arxiv | github | blog | manual
    external_id = Column(String, index=True)      # arxiv id / owner-repo / blog url — dedupe key
    author = Column(String)                       # authors / repo owner / blog author
    stars = Column(Integer)                        # github stars, refreshed on each re-sighting
    raw = Column(Text)                             # original abstract/description the script grabbed
    published_at = Column(DateTime, nullable=True)  # paper/repo/post date

    # Freshness
    last_seen_at = Column(DateTime, default=datetime.utcnow)       # last time the script re-saw it
    last_reviewed_at = Column(DateTime, nullable=True)             # last time I curated it

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    insights = relationship("Insight", back_populates="resource", cascade="all, delete-orphan")
    versions = relationship(
        "ResourceVersion",
        back_populates="resource",
        cascade="all, delete-orphan",
        order_by="ResourceVersion.changed_on.desc()",   # newest first
    )


class Insight(Base):
    """The takeaway a resource gives for one task/technique — and the link
    itself. One blog post → several insights → several tasks.

    Example: a single RAG blog might produce three insights on itself:
      • task=Data Labeling   -> "LLM-as-labeler with a verification pass"
      • task=Semantic Search -> "Semantic chunking with 15% overlap beats fixed size"
      • task=LLM Fine-tuning  -> "QLoRA on 10k pairs was enough"
    """
    __tablename__ = "insights"
    __table_args__ = (
        Index("ix_insight_task", "task_id"),
        Index("ix_insight_technique", "technique_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    technique_id = Column(Integer, ForeignKey("techniques.id", ondelete="CASCADE"), nullable=True)

    title = Column(String)          # short: "Semantic chunking with overlap"
    detail = Column(Text)           # markdown: the actual takeaway / how to use it
    # 'use'   = actionable — shown on the task's "What our sources say" shelf
    # 'study' = background — shown under the task's "Further reading", and in the Reading list
    kind = Column(String, default="use")
    created_at = Column(DateTime, default=datetime.utcnow)

    resource = relationship("Resource", back_populates="insights")
    task = relationship("Task", back_populates="insights")
    technique = relationship("Technique", back_populates="insights")


class ResourceVersion(Base):
    """One entry in a resource's version history — a plain timeline of updates:
    what changed, when, and (the part that matters) why it's useful to us."""
    __tablename__ = "resource_versions"

    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(Integer, ForeignKey("resources.id", ondelete="CASCADE"))
    version_label = Column(String)      # "v2", "0.3.0", or a date — whatever the thing calls it
    changed_on = Column(DateTime, default=datetime.utcnow)
    what_changed = Column(Text)         # the change itself
    why_it_matters = Column(Text)       # how it affects our use of it
    link = Column(String)               # release notes / new paper version, optional
    created_at = Column(DateTime, default=datetime.utcnow)

    resource = relationship("Resource", back_populates="versions")


class Experiment(Base):
    """A benchmark / experiment record for a task — the optional 'try it' layer."""
    __tablename__ = "experiments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"))
    dataset = Column(String)        # what it was run on
    metric = Column(String)         # what was measured (e.g. "MAPE", "F1")
    results = Column(Text)          # markdown: table of technique -> score, notes
    code_link = Column(String)      # notebook / repo
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    task = relationship("Task", back_populates="experiments")


class ChangeLog(Base):
    """A lightweight activity feed — only here to build the daily digest.
    'What did we add or change today?' is just the rows from today."""
    __tablename__ = "changelog"
    __table_args__ = (
        Index("ix_changelog_created", "created_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String, index=True)   # task | technique | resource | insight | experiment
    entity_id = Column(Integer, index=True)
    entity_name = Column(String)                # denormalized label so the digest reads without joins
    kind = Column(String)                        # added | updated | version | insight | linked
    note = Column(Text)                          # human-readable "what happened"
    created_at = Column(DateTime, default=datetime.utcnow)
