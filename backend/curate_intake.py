#!/usr/bin/env python3
"""One-off curation of the 2026-09-23 intake batch.

Each item is triaged into one of three fates:
  - ACTIONABLE -> reviewed + summary + insight(s) linked to task(s)  ("use at office")
  - STUDY      -> reviewed + summary, NO task insight                 (goes to Reading list)
  - ARCHIVE    -> archived (noise: personal projects, PR, off-topic)
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

# id -> (status, summary, [ (task_slug, insight_title, insight_detail), ... ])
ACTIONABLE = {
    31: ("A calibrated text-classification transformer (system-one, RLCD-style calibrated decisions). "
         "A ready model to try when you need confident, well-calibrated class probabilities.",
         [("text-classification", "Calibration-aware classifier model",
           "Off-the-shelf transformer tuned for calibrated decisions — worth a look when miscalibrated confidence is the pain point, not raw accuracy.")]),
    32: ("A 2-bit *ternary* GGUF quantization of a 27B LLM, runnable via llama.cpp on modest hardware.",
         [("model-quantization", "2-bit ternary quantization in the wild",
           "Concrete example of pushing a 27B model to ~2-bit ternary (GGUF/llama.cpp) — reference point for how far quantization can go before quality breaks.")]),
    33: ("Qwen-Image-2.1 — a strong open text-to-image model that also does image editing (diffusers, RGBA).",
         [("text-to-image-generation", "Open T2I model with editing",
           "Candidate open model when a text-to-image need lands; notably also supports editing/inpainting in the same weights."),
          ("image-editing-inpainting", "Editing from the same T2I model",
           "One model covers both generation and edits — fewer moving parts than a separate inpainting pipeline.")]),
    34: ("How UK AISI + EvalEval make benchmark results reproducible — practices for trustworthy eval reporting.",
         [("llm-evaluation", "Make benchmark results reproducible",
           "Checklist-style practices (fixed seeds, versioned data, transparent harness) so your eval numbers hold up and are comparable run-to-run.")]),
    35: ("HF Transformers can now load llama.cpp GGUF quantized weights directly — one loader for quantized models.",
         [("model-quantization", "Load GGUF quants straight from Transformers",
           "No separate llama.cpp path: load a GGUF quantized model inside the Transformers API you already use — simplifies serving quantized LLMs.")]),
    37: ("ABBEL: instead of stuffing the full history into context, the agent keeps graded 'beliefs' as working memory for long-horizon tasks.",
         [("llm-agents-tool-use", "Belief state beats recursive summarization",
           "For long-running agents, replace the growing transcript with a compact, graded belief store — cheaper context and better long-horizon performance than summarizing history.")]),
    44: ("A practical LLM security workflow: build a threat model, find vulns, verify, triage, patch.",
         [("llm-agents-tool-use", "LLM-driven code security loop",
           "Reusable pattern for a code-review/security agent: threat-model → discover → verify → triage → patch, with the LLM in each step.")]),
    45: ("Product evals in three steps: label some data, align LLM-evaluators to your labels, run the harness on every change.",
         [("llm-evaluation", "A minimal product-eval loop",
           "The pragmatic recipe: hand-label a small set, calibrate an LLM-judge against it, then gate every change through the harness. Good default when starting evals from zero.")]),
    11: ("ModelBrief — Python library that auto-generates structured reports of ML experiment results (performance, key insights).",
         [("experiment-tracking", "Auto-reporting for experiments",
           "Generates readable experiment reports automatically — a lightweight complement to a tracker when you need shareable summaries, not just logged metrics.")]),
    19: ("loci — a ~300-line 'second brain': hybrid retrieval (vector + BM25), section-level citations, MCP server, no LangChain.",
         [("semantic-search-rag", "Minimal hybrid-retrieval RAG reference",
           "Compact reference for doing RAG right: vector + BM25 hybrid with section-level citations in ~300 lines. Great to read when you want retrieval without a heavy framework.")]),
    21: ("nibble — a Go library for splitting long text into retrieval-sized chunks for RAG.",
         [("semantic-search-rag", "Chunking library (Go)",
           "If your stack is Go, a ready chunker for RAG ingestion. Language-specific, but saves rolling your own splitter.")]),
    22: ("InternLumina-U2 — a multi-codebook diffusion LLM for omni-visual understanding, image generation and editing (InternLM).",
         [("vision-language-models", "Unified understand+generate multimodal model",
           "From a reputable lab: one model spanning visual understanding and image gen/editing — candidate when a task needs both perception and generation.")]),
    24: ("npuforge — convert a Stable Diffusion 1.5/SDXL checkpoint into a Qualcomm NPU model on the phone itself (supports LoRA merging).",
         [("model-serving-inference", "On-device diffusion on Qualcomm NPU",
           "Path to run diffusion models fully on-device (phone NPU), no PC/server — relevant for edge/on-device image generation.")]),
    25: ("timeseries-atlas — a curated map of modern time-series forecasting architectures, each with a short README and runnable code.",
         [("forecasting", "Shortlist of modern forecasting architectures",
           "Exactly the 'what do I reach for' reference: a browsable atlas of current forecasting models with runnable code. Start here when a forecasting task lands.")]),
    27: ("tsforge — automatic time-series analysis, forecasting and reporting.",
         [("forecasting", "AutoML-style forecasting tool",
           "Automates the analyze→forecast→report loop; good fast baseline before hand-tuning a forecaster.")]),
    30: ("loop-computer-vision — a CV pipeline that tracks vehicles and people in traffic footage and reports counts + congestion.",
         [("video-understanding", "Tracking + counting reference pipeline",
           "Concrete detection→tracking→counting pipeline; useful reference when a 'count/track objects in video' task comes up.")]),
    13: ("halo (White Circle) — an open-source framework for training large language and multimodal models.",
         [("llm-fine-tuning-adaptation", "Another LLM/multimodal training framework",
           "Early-stage framework to watch for training LLM/multimodal models; validate maturity before betting on it.")]),
}

STUDY = {
    4:  "GameHorizon Suite — a multi-horizon dataset + evaluation for gameplay AI (visual understanding, planning, action control). Research reference for long-horizon agent evaluation.",
    5:  "VideoGen-Agent — reinforcing video-generation agents to satisfy specialized/identity/physics constraints. Frontier video-gen research; background reading.",
    6:  "Critical-State RL — diagnosing which single model call in a multi-turn tool-use trajectory is actually trainable. Research on where to spend RL signal in agents.",
    7:  "SkillSpec — intent-masked specification reasoning to check agent 'skill' correctness. Research on making reusable agent skills reliable.",
    8:  "The Functionalizer — lossless functional decomposition for subword tokenization (handles case/accents without fragmenting the embedding space). Tokenization research.",
    9:  "Realtime-Venus — a full-duplex (talk-and-listen) interaction system with asynchronous delegation, grounding dialogue in audio+video. Speech/multimodal interaction research.",
    36: "From CUDA to MLX — translating GPU kernel-optimization knowledge into Apple-Silicon-native MLX strategies. Deep systems/perf reading for on-device acceleration.",
    40: "OpenAI introduces GPT-6 Sol and Luna — frontier models balancing capability vs cost. Market-awareness: know what's newly available.",
    42: "distill.pub — Understanding Convolutions on Graphs. Excellent visual explainer of GNN building blocks. Best-in-class study material.",
    43: "distill.pub — A Gentle Introduction to Graph Neural Networks. The canonical intro to GNNs; read before touching graph ML.",
    46: "Lilian Weng — Harness Engineering for Self-Improvement. Essay on recursive self-improvement and agent harnesses. Conceptual reading.",
    47: "Lilian Weng — Scaling Laws, Carefully. Careful treatment of how loss scales with model/data/compute. Foundational understanding for training decisions.",
    14: "titania — a complete LLM 'from transformer to transistor', small enough for one person to understand. Superb for studying LLM internals end to end.",
    15: "One-Shot-OPD — rethinking on-policy distillation of LLMs from a single training example. Research code for distillation study.",
    16: "reef — continual-learning infrastructure for self-improving agents. Early infra to study for long-lived agents.",
    26: "RuForecast — multivariate time-series forecasting in Rust (Burn, CPU/CUDA/WGPU), privacy-governed. Watch/awareness for Rust-based forecasting.",
    23: "ALIGN — agentic-loop image generation WITHOUT diffusion/autoregressive models: coding agents draw in p5.js with iterative adversarial review. Novel approach worth understanding.",
}

ARCHIVE = {
    38: "Google 'AI for Societal Impact' — a marketing collection, no technique.",
    39: "Google dialogue with an astronaut — off-topic PR.",
    41: "Higgsfield/OpenAI customer story — marketing, no reusable method.",
    10: "Vague personal 'AI learning toolkit', no clear reference value.",
    12: "cadence — vague 'consensus equilibrium world models', no substance to act on.",
    17: "Personal WeChat/QQ chat copilot — personal project, off-scope.",
    18: "BrowserKitten — personal web-agent product, low reference value.",
    20: "eidra-agent — vague persona-agent personal project.",
    28: "'Fun CV demos' — no reference value.",
    29: "jev-use — personal Mac computer-use toy.",
}


def main():
    db = SessionLocal()
    now = datetime.utcnow()
    counts = {"actionable": 0, "study": 0, "archive": 0, "insights": 0, "missing": 0}
    try:
        tasks = {t.slug: t for t in db.query(models.Task).all()}

        def get(rid):
            return db.query(models.Resource).get(rid)

        for rid, (summary, insights) in ACTIONABLE.items():
            r = get(rid)
            if not r:
                counts["missing"] += 1; continue
            r.summary = summary; r.status = "reviewed"; r.last_reviewed_at = now
            for slug, title, detail in insights:
                task = tasks.get(slug)
                if not task:
                    print(f"  ! no task slug '{slug}' for #{rid}"); continue
                db.add(models.Insight(resource_id=r.id, task_id=task.id, title=title, detail=detail))
                counts["insights"] += 1
                log_change(db, "insight", r.id, title, "insight", f"'{r.title}' → {task.name}")
            counts["actionable"] += 1

        for rid, summary in STUDY.items():
            r = get(rid)
            if not r:
                counts["missing"] += 1; continue
            r.summary = summary; r.status = "reviewed"; r.last_reviewed_at = now
            log_change(db, "resource", r.id, r.title, "updated", "Filed to Reading list (study)")
            counts["study"] += 1

        for rid, reason in ARCHIVE.items():
            r = get(rid)
            if not r:
                counts["missing"] += 1; continue
            r.status = "archived"; r.summary = r.summary or reason; r.last_reviewed_at = now
            counts["archive"] += 1

        db.commit()
    except Exception as e:
        db.rollback(); print("ERROR:", e); raise
    finally:
        db.close()

    print("Curation complete:")
    for k, v in counts.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
