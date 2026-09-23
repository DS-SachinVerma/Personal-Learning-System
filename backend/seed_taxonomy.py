#!/usr/bin/env python3
"""Seed the ML Technique Library with a rich task taxonomy.

Tasks are the hub ("what kind of job landed on my desk?"), grouped into domains
for browsing. Techniques and sources are added via curation; this file also
plants worked examples — including a blog that gives DIFFERENT takeaways to
several tasks — so insights, version history and the daily digest all have
something to show on first run.

Idempotent: re-running skips anything whose slug/external_id already exists.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
from app.database import SessionLocal, engine
from app import models
from app.deps import slugify, log_change

models.Base.metadata.create_all(bind=engine)

# domain -> [(task name, one-liner), ...]
TAXONOMY = {
    "NLP & LLMs": [
        ("Text Classification", "Assign labels to documents — spam, intent, topic, routing."),
        ("Named Entity Recognition", "Pull out people, orgs, dates, products from raw text."),
        ("Text Summarization", "Condense long text into short abstractive or extractive summaries."),
        ("Machine Translation", "Translate text between languages."),
        ("Question Answering", "Answer questions from a passage or knowledge base."),
        ("Semantic Search / RAG", "Retrieve relevant chunks and ground an LLM answer on them."),
        ("Text Embeddings", "Turn text into vectors for search, clustering, dedup."),
        ("Topic Modeling", "Discover latent themes across a corpus."),
        ("Information Extraction", "Structure messy text into fields, tables, relations."),
        ("LLM Fine-tuning & Adaptation", "Adapt a base model to your domain (LoRA, SFT, RLHF)."),
        ("LLM Agents & Tool Use", "Let an LLM plan, call tools, and act in loops."),
        ("Prompt Engineering & Optimization", "Systematically design and tune prompts."),
        ("Text Generation", "Produce fluent text — drafting, rewriting, code."),
        ("Sentiment & Emotion Analysis", "Score tone, opinion, and emotion in text."),
    ],
    "Computer Vision": [
        ("Image Classification", "Assign one or more labels to an image."),
        ("Object Detection", "Locate and label objects with bounding boxes."),
        ("Image Segmentation", "Label every pixel — semantic, instance, panoptic."),
        ("OCR / Document AI", "Read text and structure from scanned documents."),
        ("Pose Estimation", "Detect body/hand/keypoint positions."),
        ("Face Detection & Recognition", "Find and identify faces."),
        ("Image Retrieval / Similarity", "Find visually similar images by embedding."),
        ("Depth Estimation", "Predict per-pixel distance from a camera."),
        ("Video Understanding", "Recognize actions and events across frames."),
    ],
    "Generative Models": [
        ("Text-to-Image Generation", "Create images from prompts (diffusion, etc.)."),
        ("Image Editing / Inpainting", "Edit, extend, or fill parts of an image."),
        ("Video Generation", "Generate or animate video clips."),
        ("Audio / Music Generation", "Synthesize speech, sound effects, or music."),
        ("3D Generation", "Produce 3D assets or scenes from text/images."),
    ],
    "Multimodal": [
        ("Vision-Language Models", "Joint reasoning over images and text."),
        ("Image Captioning", "Describe an image in natural language."),
        ("Visual Question Answering", "Answer questions about an image."),
        ("Cross-modal Retrieval", "Search images with text and vice versa (CLIP-style)."),
        ("Document Understanding", "Reason over layout + text + images together."),
    ],
    "Tabular & Classical ML": [
        ("Classification", "Predict a category from structured features."),
        ("Regression", "Predict a continuous value from structured features."),
        ("Feature Engineering", "Craft informative features from raw columns."),
        ("Feature Selection", "Keep the features that matter, drop the rest."),
        ("Gradient Boosting", "Strong default for tabular — XGBoost/LightGBM/CatBoost."),
        ("AutoML", "Automate model + hyperparameter search."),
        ("Imbalanced Learning", "Handle rare-class problems (fraud, defects)."),
        ("Clustering", "Group unlabeled records by similarity."),
        ("Dimensionality Reduction", "Compress features for viz or modeling."),
        ("Anomaly Detection (Tabular)", "Flag outliers in structured data."),
    ],
    "Time Series": [
        ("Forecasting", "Predict future values from history."),
        ("Time-Series Anomaly Detection", "Spot abnormal points or windows in signals."),
        ("Changepoint Detection", "Find where the behavior of a series shifts."),
        ("Time-Series Classification", "Label whole sequences (ECG, sensor traces)."),
    ],
    "Recommender Systems": [
        ("Collaborative Filtering", "Recommend from user-item interaction patterns."),
        ("Content-Based Recommendation", "Recommend by item features/embeddings."),
        ("Learning-to-Rank", "Order candidates by relevance."),
        ("Sequential Recommendation", "Predict the next item in a session."),
    ],
    "Speech & Audio": [
        ("Speech Recognition (ASR)", "Transcribe speech to text."),
        ("Text-to-Speech (TTS)", "Synthesize natural speech from text."),
        ("Speaker Diarization", "Figure out who spoke when."),
        ("Audio Classification", "Tag sounds, scenes, or events."),
    ],
    "Graph ML": [
        ("Node Classification", "Label nodes using graph structure."),
        ("Link Prediction", "Predict missing or future edges."),
        ("Graph Embeddings", "Vectorize nodes/graphs for downstream tasks."),
        ("Graph Neural Networks", "Learn directly over graph-structured data."),
    ],
    "Reinforcement Learning": [
        ("Policy Optimization", "Learn control policies via reward (PPO, SAC)."),
        ("Offline RL", "Learn policies from logged data, no live env."),
        ("Multi-Armed Bandits", "Balance explore/exploit for online decisions."),
        ("Multi-Agent RL", "Learn among multiple interacting agents."),
    ],
    "Causal Inference & Experimentation": [
        ("A/B Testing & Experiment Design", "Design and read online experiments."),
        ("Uplift / Treatment-Effect Modeling", "Estimate who is moved by an intervention."),
        ("Causal Discovery", "Infer causal structure from data."),
    ],
    "Optimization & Efficiency": [
        ("Hyperparameter Optimization", "Search configs efficiently (Optuna, BO)."),
        ("Model Quantization", "Shrink models to int8/4-bit for cheap inference."),
        ("Model Pruning", "Remove weights/structure to speed up models."),
        ("Knowledge Distillation", "Train a small model to mimic a big one."),
        ("Distributed / Accelerated Training", "Scale training across GPUs/nodes."),
    ],
    "MLOps & Infrastructure": [
        ("Experiment Tracking", "Log runs, params, metrics, artifacts."),
        ("Model Serving & Inference", "Deploy models behind fast, scalable APIs."),
        ("Feature Stores", "Serve consistent features to train and prod."),
        ("Model Monitoring & Drift Detection", "Watch live models for decay."),
        ("Pipeline Orchestration", "Schedule and wire ML/data pipelines."),
        ("Vector Databases", "Store and search embeddings at scale."),
        ("Model Registry & Versioning", "Track model lineage and promotions."),
    ],
    "Data Engineering & Prep": [
        ("Data Validation & Quality", "Catch bad data before it hits models."),
        ("Data Labeling & Annotation", "Produce labels efficiently and consistently."),
        ("Data Augmentation", "Expand datasets with transformations."),
        ("Synthetic Data Generation", "Generate realistic data when real is scarce."),
    ],
    "Evaluation, Interpretability & Responsible AI": [
        ("Model Explainability", "Explain predictions (SHAP, LIME, attributions)."),
        ("LLM Evaluation", "Score LLM/RAG quality, factuality, safety."),
        ("Fairness & Bias Detection", "Measure and mitigate biased outcomes."),
        ("Robustness & Adversarial Testing", "Stress-test models against attacks/shift."),
    ],
}


def get_or_create_task(db, name, domain, one_liner):
    slug = slugify(name)
    t = db.query(models.Task).filter(models.Task.slug == slug).first()
    if t:
        return t, False
    t = models.Task(name=name, slug=slug, domain=domain, one_liner=one_liner)
    db.add(t)
    db.flush()
    return t, True


def get_or_create_technique(db, name, summary, maturity, tasks, tags=""):
    slug = slugify(name)
    tech = db.query(models.Technique).filter(models.Technique.slug == slug).first()
    if tech:
        return tech, False
    tech = models.Technique(name=name, slug=slug, summary=summary, maturity=maturity, tags=tags)
    tech.tasks = tasks
    db.add(tech)
    db.flush()
    return tech, True


def resource_exists(db, source, external_id):
    return (
        db.query(models.Resource)
        .filter(models.Resource.source == source, models.Resource.external_id == external_id)
        .first()
    )


def main():
    db = SessionLocal()
    try:
        created_tasks = 0
        T = {}  # name -> Task
        for domain, items in TAXONOMY.items():
            for name, one_liner in items:
                task, is_new = get_or_create_task(db, name, domain, one_liner)
                T[name] = task
                created_tasks += int(is_new)
        db.flush()

        # ---- worked example: cross-task technique (overlap handling) ----
        get_or_create_technique(
            db, "XGBoost",
            summary=("**Gradient-boosted trees.** The reliable default for tabular problems.\n\n"
                     "- **Use when:** structured/tabular data, need strong accuracy fast.\n"
                     "- **Pros:** handles mixed types, robust, great baselines.\n"
                     "- **Gotchas:** tune `max_depth`/`learning_rate`; not for raw text/images."),
            maturity="proven", tags="tabular,trees,baseline",
            tasks=[T["Gradient Boosting"], T["Classification"], T["Regression"]],
        )
        sbert, _ = get_or_create_technique(
            db, "Sentence-BERT (SBERT)",
            summary=("**Transformer sentence embeddings.** Cosine similarity of the vectors tracks "
                     "meaning.\n\n- **Use when:** semantic search, RAG retrieval, clustering, dedup.\n"
                     "- **Pros:** fast, strong off-the-shelf models.\n"
                     "- **Gotchas:** pick a model matched to your domain/length."),
            maturity="proven", tags="nlp,embeddings,retrieval",
            tasks=[T["Text Embeddings"], T["Semantic Search / RAG"], T["Clustering"]],
        )

        # ---- worked example: a REPO with version history + one insight ----
        if not resource_exists(db, "github", "UKPLab/sentence-transformers"):
            repo = models.Resource(
                title="sentence-transformers", type="repo",
                link="https://github.com/UKPLab/sentence-transformers",
                summary="Library for SBERT-style embeddings: load a model, `.encode()`, compare vectors.",
                tags="nlp,embeddings,retrieval", status="reviewed", source="github",
                external_id="UKPLab/sentence-transformers", author="UKPLab", stars=15000,
                last_reviewed_at=datetime.utcnow(),
            )
            db.add(repo); db.flush()
            db.add(models.Insight(
                resource_id=repo.id, task_id=T["Semantic Search / RAG"].id, technique_id=sbert.id,
                title="Drop-in retrieval encoder",
                detail="Use `all-MiniLM-L6-v2` for a fast first-pass retriever; swap to a larger model only if recall is short.",
            ))
            db.add(models.ResourceVersion(
                resource_id=repo.id, version_label="v3.0", changed_on=datetime.utcnow() - timedelta(days=40),
                what_changed="Multi-loss training + better ONNX export.",
                why_it_matters="Cheaper CPU inference for our retrieval service via ONNX.",
                link="https://github.com/UKPLab/sentence-transformers/releases",
            ))
            db.add(models.ResourceVersion(
                resource_id=repo.id, version_label="v2.2", changed_on=datetime.utcnow() - timedelta(days=300),
                what_changed="More efficient community-detection clustering utilities.",
                why_it_matters="Lets us dedup near-duplicate docs before indexing.",
            ))
            log_change(db, "resource", repo.id, repo.title, "added", "Seed example: repo with version history")

        # ---- worked example: a BLOG that feeds THREE different tasks ----
        # (exactly the case you described: one source, many tasks, a takeaway each)
        if not resource_exists(db, "blog", "example.com/building-production-rag"):
            blog = models.Resource(
                title="Lessons from Building a Production RAG System", type="blog",
                link="https://example.com/building-production-rag",
                summary="A field report on shipping RAG — covers data prep, chunking, and retrieval choices.",
                tags="rag,nlp,retrieval,dataset", status="reviewed", source="blog",
                external_id="example.com/building-production-rag", author="Some ML Engineer",
                last_reviewed_at=datetime.utcnow(),
            )
            db.add(blog); db.flush()
            db.add(models.Insight(
                resource_id=blog.id, task_id=T["Data Labeling & Annotation"].id,
                title="LLM-as-labeler with a verification pass",
                detail="Bootstrap labels with an LLM, then have a second model/human verify a 10% sample to catch drift.",
            ))
            db.add(models.Insight(
                resource_id=blog.id, task_id=T["Semantic Search / RAG"].id,
                title="Semantic chunking beats fixed-size",
                detail="Chunk on semantic boundaries with ~15% overlap; measured a real jump in answer relevance vs. fixed 512-token splits.",
            ))
            db.add(models.Insight(
                resource_id=blog.id, task_id=T["LLM Fine-tuning & Adaptation"].id,
                title="QLoRA was enough",
                detail="~10k curated pairs + QLoRA matched full fine-tuning for their domain, at a fraction of the cost.",
            ))
            log_change(db, "resource", blog.id, blog.title, "added",
                       "Seed example: one blog → 3 tasks (dataset, chunking, fine-tuning)")

        # ---- worked example: a foundational PAPER ----
        if not resource_exists(db, "arxiv", "1706.03762"):
            paper = models.Resource(
                title="Attention Is All You Need", type="paper",
                link="https://arxiv.org/abs/1706.03762",
                summary="The Transformer paper — the architecture under nearly every modern NLP/LLM technique.",
                tags="transformers,nlp,foundational", status="reviewed", source="arxiv",
                external_id="1706.03762", author="Vaswani et al.", last_reviewed_at=datetime.utcnow(),
            )
            db.add(paper); db.flush()
            db.add(models.Insight(
                resource_id=paper.id, task_id=T["Text Generation"].id,
                title="Why attention replaced recurrence",
                detail="Self-attention gives parallel training + long-range context — the reason transformers scaled.",
            ))
            log_change(db, "resource", paper.id, paper.title, "added", "Seed example: foundational paper")

        db.commit()
        print(f"OK. Tasks: {db.query(models.Task).count()} (+{created_tasks} new) across {len(TAXONOMY)} domains")
        print(f"    Techniques: {db.query(models.Technique).count()}   "
              f"Resources: {db.query(models.Resource).count()}   "
              f"Insights: {db.query(models.Insight).count()}")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
