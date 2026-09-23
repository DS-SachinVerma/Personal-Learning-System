#!/usr/bin/env python3
"""Tie study-list resources to the tasks they're about, as kind='study' insights.

These do NOT clutter a task's actionable shelf — the UI shows them under a
separate "Further reading" lane. Items with no single clear task home are left
untied (they still live in the Reading list).
"""
import sys, os
from datetime import datetime
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import models
from app.deps import log_change

# resource_id -> (task_slug, short reading-note)
TIES = {
    42: ("graph-neural-networks", "Visual explainer of GNN building blocks — start here before graph ML."),
    43: ("graph-neural-networks", "The canonical gentle intro to GNNs."),
    5:  ("video-generation", "Frontier research on constraining video-gen agents."),
    6:  ("llm-agents-tool-use", "Where to spend RL signal across a multi-turn tool-use trajectory."),
    7:  ("llm-agents-tool-use", "Making reusable agent 'skills' verifiably correct."),
    16: ("llm-agents-tool-use", "Continual-learning infra for long-lived, self-improving agents."),
    46: ("llm-agents-tool-use", "Essay on recursive self-improvement and agent harnesses."),
    8:  ("text-embeddings", "Tokenization that stops case/accents from fragmenting the embedding space."),
    36: ("distributed-accelerated-training", "Translating CUDA kernel know-how to Apple-Silicon MLX."),
    47: ("distributed-accelerated-training", "How loss scales with model/data/compute — read before big training runs."),
    15: ("knowledge-distillation", "Rethinking on-policy distillation from a single example."),
    14: ("text-generation", "An LLM built from scratch, small enough to fully understand."),
    26: ("forecasting", "Rust-based multivariate forecasting — awareness/watch."),
    23: ("text-to-image-generation", "Novel agentic image generation without diffusion (p5.js + adversarial review)."),
}
# left untied on purpose: 4 (game eval, no clear home), 9 (full-duplex speech), 40 (GPT-6 news)


def main():
    db = SessionLocal()
    now = datetime.utcnow()
    tasks = {t.slug: t for t in db.query(models.Task).all()}
    tied = 0
    try:
        for rid, (slug, note) in TIES.items():
            r = db.query(models.Resource).get(rid)
            task = tasks.get(slug)
            if not r or not task:
                print(f"  ! skip #{rid} ({slug})"); continue
            # avoid duplicate study links if re-run
            exists = db.query(models.Insight).filter_by(
                resource_id=rid, task_id=task.id, kind="study").first()
            if exists:
                continue
            db.add(models.Insight(resource_id=rid, task_id=task.id, kind="study",
                                  title="Further reading", detail=note))
            log_change(db, "insight", rid, r.title, "insight", f"study → {task.name}")
            tied += 1
        db.commit()
        print(f"Tied {tied} study resource(s) to tasks.")
    except Exception as e:
        db.rollback(); print("ERROR:", e); raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
