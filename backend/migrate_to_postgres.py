#!/usr/bin/env python3
"""One-shot: finish the last 2 summaries, then copy SQLite -> Postgres.

Source = local SQLite file. Destination = the app engine (Postgres, from .env).
Copies every table in FK-safe order preserving ids, then fixes the Postgres
id sequences. Aborts if the destination already has data.
"""
import sys, os
from datetime import datetime
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app import models
from app.database import engine as dest, DATABASE_URL

SRC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "learning_tracker.db")
src = create_engine(f"sqlite:///{SRC_PATH}")
meta = models.Base.metadata
R = models.Resource.__table__

SUMMARY_1 = """**sentence-transformers — the standard library for turning text into embeddings you can compare.**

**What it is** — A Python library (originally UKPLab/SBERT, now maintained under the Hugging Face org) that wraps transformer models to produce dense sentence/paragraph embeddings whose cosine similarity tracks meaning. Ships hundreds of pretrained models behind a one-call `model.encode()` API.

**How it works / key ideas**
- Fine-tunes transformers with siamese/triplet objectives so similar texts land close in vector space.
- `encode()` returns (optionally normalized) vectors; helpers for semantic search, clustering, paraphrase mining, and cross-encoder re-ranking.
- Lets you fine-tune your own embeddings and export to ONNX for cheap CPU inference.

**Where we'd use it**
- The retrieval layer of any RAG / semantic-search feature (embed docs + query, cosine top-k).
- De-duplicating or clustering large text corpora before indexing.
- A fast, cheap similarity/rerank signal inside a larger pipeline.

**Strengths** — Battle-tested, huge model zoo, trivial API, strong CPU/ONNX story, permissive license.
**Caveats** — Match the model to your domain/length; long-doc and multilingual needs specific checkpoints; quality is capped by the base model.
**Maturity / adoption** — Proven; ~15k+ GitHub stars, the de-facto default for open-source text embeddings."""

SUMMARY_2 = """**Illustrative field-report on shipping production RAG — a seed example showing how one source can feed several tasks.**

**What it is** — A placeholder resource (non-resolving URL) used to demonstrate the library's core idea: a single write-up that yields a *different* takeaway for *different* tasks. It carries three insights across Data Labeling, Semantic Search/RAG, and Fine-tuning.

**Key ideas it illustrates**
- **Data labeling:** bootstrap labels with an LLM, then verify a ~10% sample.
- **Retrieval:** semantic chunking with ~15% overlap beat fixed 512-token splits on answer relevance.
- **Adaptation:** QLoRA on ~10k curated pairs matched full fine-tuning at a fraction of the cost.

**Where we'd use it** — As the worked example on those three task pages, showing how insights cross-link back to one source.

**Strengths** — Concrete demonstration of the one-source-many-tasks model.
**Caveats** — Seed/demo data with a non-resolving URL; replace with real field reports as they're collected.
**Maturity / adoption** — N/A (illustrative seed)."""


def main():
    if not DATABASE_URL.startswith("postgresql"):
        print("Refusing: DATABASE_URL is not Postgres:", DATABASE_URL.split("://")[0]); return
    print("Destination:", DATABASE_URL.split("@")[-1].split("/")[0])

    # guard: don't double-migrate
    with dest.connect() as c:
        if c.execute(text("SELECT COUNT(*) FROM tasks")).scalar():
            print("Destination already has data in 'tasks' — aborting to avoid duplicates.")
            return

    # 1) finish the last two summaries in the source
    with src.begin() as s:
        s.execute(R.update().where(R.c.id == 1).values(summary=SUMMARY_1))
        s.execute(R.update().where(R.c.id == 2).values(summary=SUMMARY_2))
    print("Wrote summaries for resources 1 and 2.")

    # 2) copy every table in FK-safe order, preserving ids
    for table in meta.sorted_tables:
        with src.connect() as s:
            rows = [dict(r._mapping) for r in s.execute(table.select())]
        if not rows:
            print(f"  {table.name:18} 0 (empty)"); continue
        with dest.begin() as d:
            d.execute(table.insert(), rows)
        print(f"  {table.name:18} {len(rows)}")

    # 3) fix id sequences so future inserts don't collide
    with dest.begin() as d:
        for table in meta.sorted_tables:
            if "id" in table.c:
                seq = d.execute(text("SELECT pg_get_serial_sequence(:t, 'id')"), {"t": table.name}).scalar()
                if seq:
                    d.execute(text(f"SELECT setval('{seq}', COALESCE((SELECT MAX(id) FROM {table.name}), 1))"))
    print("Sequences reset.")

    # 4) verify
    with dest.connect() as c:
        for t in ("tasks", "techniques", "resources", "insights", "resource_versions", "experiments", "changelog"):
            n = c.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar()
            print(f"  [pg] {t:18} {n}")
        rich = c.execute(text("SELECT COUNT(*) FROM resources WHERE summary IS NOT NULL AND summary <> ''")).scalar()
        print(f"  [pg] resources with summary: {rich}")
    print("Migration complete.")


if __name__ == "__main__":
    main()
