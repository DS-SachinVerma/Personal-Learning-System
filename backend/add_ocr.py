#!/usr/bin/env python3
"""Curate the OCR / Document AI batch (idempotent)."""
import sys, os
from datetime import datetime
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import models
from app.deps import slugify, log_change

TECHS = [
    ("Deep OCR Pipeline (Detect + Recognize)", "proven", "ocr,cv,document",
     ["ocr-document-ai"],
     "**Two-stage classic OCR:** detect text regions, then recognize the characters in each.\n\n"
     "- **Use when:** you need robust, fast, multilingual text extraction from images/PDFs.\n"
     "- **Pros:** mature, lightweight, 100+ languages (PaddleOCR); runs on CPU.\n"
     "- **Gotchas:** complex layouts/tables need a separate layout step; weaker on handwriting."),
    ("Vision-Language Document Parsing", "proven", "ocr,vlm,document,multimodal",
     ["ocr-document-ai", "document-understanding"],
     "**A single vision-language model reads the page image and emits structured markdown/JSON** — "
     "text, tables, and reading order together, with no separate OCR stage.\n\n"
     "- **Use when:** complex layouts (tables, multi-column, forms) where classic OCR loses structure.\n"
     "- **Current wave:** Qwen-VL / GLM-OCR / LFM2-VL fine-tunes, and dots.ocr, Dolphin, Jina-OCR.\n"
     "- **Pros:** handles layout + reading order in one model; strong on messy docs.\n"
     "- **Gotchas:** GPU cost; can hallucinate — verify numbers/totals against a second pass."),
    ("Document-to-Markdown Conversion", "proven", "document,parsing,rag,etl",
     ["ocr-document-ai"],
     "**Turn PDFs/Office docs into clean, LLM-ready markdown/JSON** (layout parse + extraction). "
     "The standard front-end to RAG over documents.\n\n"
     "- **Use when:** feeding real-world documents into a RAG or extraction pipeline.\n"
     "- **Tools:** MinerU, unstructured, liteparse.\n"
     "- **Pros:** one step from raw doc to chunk-ready text; preserves structure.\n"
     "- **Gotchas:** tables and scanned (vs digital) PDFs are where quality varies most."),
]

# resource_id -> (summary, kind, task_slug, technique_slug|None, insight_title, insight_detail)
USE = {
    48: ("**PaddleOCR** — batteries-included, lightweight OCR toolkit; 100+ languages; PDF/image → structured data for LLMs.",
         "ocr-document-ai", "deep-ocr-pipeline-detect-recognize", "Default multilingual OCR toolkit",
         "The go-to open OCR when you need broad language coverage and CPU-friendly speed; PDF/image → structured data out of the box."),
    49: ("**MinerU** — transforms complex PDFs/Office docs into LLM-ready markdown/JSON for agentic workflows.",
         "ocr-document-ai", "document-to-markdown-conversion", "PDF/Office → LLM-ready markdown",
         "Strong first choice to convert messy documents to clean markdown/JSON before RAG or extraction."),
    51: ("**unstructured** — open-source ETL that converts complex documents into clean structured formats for language models.",
         "ocr-document-ai", "document-to-markdown-conversion", "Document ETL for LLMs",
         "Broad connector/format support; good when you need a general document-ingestion ETL, not just one file type."),
    52: ("**liteparse** (LlamaIndex) — a fast, open-source document parser.",
         "ocr-document-ai", "document-to-markdown-conversion", "Fast lightweight parser",
         "Lighter/faster option in the doc-to-markdown space; worth benchmarking against MinerU on your docs."),
    53: ("**zerox** — OCR & document extraction using vision models (pass a page image to a VLM, get markdown).",
         "ocr-document-ai", "vision-language-document-parsing", "Simple VLM-OCR wrapper",
         "Minimal way to try the VLM-OCR approach: hand a page image to a vision model and get markdown back."),
    54: ("**dots.ocr** — multilingual document *layout* parsing inside a single vision-language model.",
         "ocr-document-ai", "vision-language-document-parsing", "Layout parsing in one VLM",
         "Does layout + text in one model across languages — reach for it when structure/reading-order matters."),
    55: ("**Dolphin** (ByteDance, ACL 2025) — document image parsing via heterogeneous anchor prompting.",
         "ocr-document-ai", "vision-language-document-parsing", "Anchor-prompted doc parsing",
         "Research-backed VLM parser; anchor prompting improves structured extraction from document images."),
    63: ("**Jina-OCR-v1** — end-to-end document parsing model built to serve on low-budget GPUs (compressed-vision encoder + small MoE decoder).",
         "ocr-document-ai", "vision-language-document-parsing", "Cheap-to-serve VLM parser",
         "Notable for cost: end-to-end parsing tuned for low-budget GPUs — candidate when VLM-OCR must be affordable to run."),
}

# resource_id -> (summary, task_slug)   [study — Reading list, tied to task]
STUDY = {
    50: ("**paperless-ngx** — a full document-management system (scan, index, archive). An end-user app, not a building block.",
         "ocr-document-ai"),
    56: ("Uses redundancy within a document to self-correct OCR errors. Post-processing idea for noisy OCR.", "ocr-document-ai"),
    57: ("A framework to recover NLP accuracy when running over imperfect OCR text.", "ocr-document-ai"),
    58: ("GPT + Donut (OCR-free) for table-of-contents extraction from long specs.", "document-understanding"),
    59: ("UTRNet — high-resolution, multi-scale recognition for printed Urdu (low-resource script).", "ocr-document-ai"),
    60: ("Long-range transformer architectures for whole-document understanding.", "document-understanding"),
    61: ("Line-level OCR keeps context vs error-prone char-by-char segmentation.", "ocr-document-ai"),
    62: ("Document-specific pre-training tasks boost information extraction on business documents.", "information-extraction"),
}

ARCHIVE = list(range(64, 72))  # niche personal VLM-OCR fine-tunes (Arabic/legal/English) — low signal


def main():
    db = SessionLocal()
    now = datetime.utcnow()
    tasks = {t.slug: t for t in db.query(models.Task).all()}
    made_t = made_i = arch = 0

    def ins_exists(rid, tid):
        return db.query(models.Insight).filter_by(resource_id=rid, task_id=tid).first()

    try:
        # techniques
        for name, maturity, tags, tslugs, summary in TECHS:
            slug = slugify(name)
            if not db.query(models.Technique).filter_by(slug=slug).first():
                t = models.Technique(name=name, slug=slug, summary=summary, maturity=maturity,
                                     tags=tags, last_reviewed_at=now)
                t.tasks = [tasks[s] for s in tslugs if s in tasks]
                db.add(t); db.flush()
                log_change(db, "technique", t.id, t.name, "added", "OCR technique")
                made_t += 1
        db.flush()
        techs = {t.slug: t for t in db.query(models.Technique).all()}

        def curate(rid, summary, kind, tslug, techslug, title, detail):
            r = db.query(models.Resource).get(rid)
            if not r:
                return
            r.summary = summary; r.status = "reviewed"; r.last_reviewed_at = now
            task = tasks.get(tslug)
            if task and not ins_exists(rid, task.id):
                tech = techs.get(techslug) if techslug else None
                db.add(models.Insight(resource_id=rid, task_id=task.id,
                                      technique_id=tech.id if tech else None,
                                      kind=kind, title=title, detail=detail))
                nonlocal_counter[0] += 1

        nonlocal_counter = [0]
        for rid, (summary, tslug, techslug, title, detail) in USE.items():
            curate(rid, summary, "use", tslug, techslug, title, detail)
        for rid, (summary, tslug) in STUDY.items():
            curate(rid, summary, "study", tslug, None, "Further reading", summary)
        made_i = nonlocal_counter[0]

        for rid in ARCHIVE:
            r = db.query(models.Resource).get(rid)
            if r:
                r.status = "archived"; r.last_reviewed_at = now
                r.summary = r.summary or "Niche personal VLM-OCR fine-tune — low general signal."
                arch += 1

        db.commit()
        print(f"Techniques added: {made_t}   Insights added: {made_i}   Archived: {arch}")
        print(f"Total techniques now: {db.query(models.Technique).count()}")
    except Exception as e:
        db.rollback(); print("ERROR:", e); raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
