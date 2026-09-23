#!/usr/bin/env python3
"""Extract techniques from today's curated batch and wire them up.

For each technique: create it (dedup by slug), link it to its task(s), and tag
the already-curated insight(s) that evidence it (sets insight.technique_id) so
the technique page shows its sources and the task page shows the technique chip.
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
from app.deps import slugify, log_change

# name, maturity, tags, [task_slugs], summary(md), [(resource_id, task_slug) insights to tag]
TECHS = [
    ("Hybrid Retrieval (BM25 + Vector)", "proven", "rag,retrieval,search",
     ["semantic-search-rag"],
     "**Combine lexical (BM25) and dense-vector search, then fuse the rankings** (e.g. Reciprocal Rank Fusion).\n\n"
     "- **Use when:** retrieval recall matters and queries mix exact terms with meaning.\n"
     "- **Pros:** catches keyword hits BM25 gets *and* paraphrases vectors get.\n"
     "- **Gotchas:** tune the fusion weighting; dedup overlapping hits.",
     [(19, "semantic-search-rag")]),

    ("Semantic Chunking", "emerging", "rag,chunking,preprocessing",
     ["semantic-search-rag"],
     "**Split documents on semantic boundaries with a little overlap**, instead of fixed token windows.\n\n"
     "- **Use when:** building the ingestion side of RAG.\n"
     "- **Pros:** measurably better answer relevance than fixed 512-token splits.\n"
     "- **Gotchas:** costs an embedding pass at index time; pick overlap (~10-15%).",
     [(2, "semantic-search-rag")]),

    ("LLM-as-Judge Evaluation", "proven", "eval,llm,judge",
     ["llm-evaluation"],
     "**Use an LLM to grade outputs against criteria or reference labels.**\n\n"
     "- **Use when:** no cheap automatic metric exists (open-ended text, RAG answers).\n"
     "- **Pros:** scalable, flexible, cheap once aligned.\n"
     "- **Gotchas:** calibrate the judge to human labels first; watch position/verbosity bias.",
     [(45, "llm-evaluation")]),

    ("Belief-State Agent Memory", "experimental", "agents,memory,long-horizon",
     ["llm-agents-tool-use"],
     "**Keep compact, graded 'beliefs' as the agent's working context** instead of the full transcript.\n\n"
     "- **Use when:** long-horizon agents whose history blows up the context window.\n"
     "- **Pros:** cheaper context, better long-horizon performance than recursive summarization.\n"
     "- **Gotchas:** needs a scheme to grade/supervise belief quality.",
     [(37, "llm-agents-tool-use")]),

    ("GGUF Quantization (llama.cpp)", "proven", "quantization,inference,llama.cpp",
     ["model-quantization", "model-serving-inference"],
     "**Portable quantized weight format for cheap CPU / edge LLM inference.**\n\n"
     "- **Use when:** serving LLMs without a big GPU budget.\n"
     "- **Pros:** runs via llama.cpp and now loads directly in HF Transformers.\n"
     "- **Gotchas:** quality drops at very low bit-widths — measure on your task.",
     [(35, "model-quantization")]),

    ("Ternary / 2-bit Quantization", "experimental", "quantization,low-bit",
     ["model-quantization"],
     "**Push weights down to ~2-bit ternary values** for extreme compression.\n\n"
     "- **Use when:** you need the smallest possible footprint and can tolerate some loss.\n"
     "- **Pros:** dramatic size/memory savings.\n"
     "- **Gotchas:** accuracy loss; needs specialized kernels to run fast.",
     [(32, "model-quantization")]),

    ("Diffusion Models", "proven", "generative,diffusion,image",
     ["text-to-image-generation", "image-editing-inpainting"],
     "**Iterative denoising generative models** — the SOTA family for image generation and editing.\n\n"
     "- **Use when:** text-to-image, inpainting, editing, or on-device image gen.\n"
     "- **Pros:** high quality, strong controllability (ControlNet, LoRA).\n"
     "- **Gotchas:** sampling compute; step count trades speed vs quality.",
     [(33, "text-to-image-generation"), (24, "model-serving-inference")]),

    ("Graph Convolutional Networks (GCN)", "proven", "graph,gnn,message-passing",
     ["graph-neural-networks"],
     "**Neural message-passing over graph neighborhoods** to learn node/graph representations.\n\n"
     "- **Use when:** data is relational (social, molecules, knowledge graphs).\n"
     "- **Pros:** leverages structure classical models ignore.\n"
     "- **Gotchas:** oversmoothing with depth; scaling to huge graphs.",
     [(42, "graph-neural-networks"), (43, "graph-neural-networks")]),

    ("On-Policy Distillation", "experimental", "distillation,training",
     ["knowledge-distillation"],
     "**Distil using the student's own on-policy samples**, not only fixed teacher outputs.\n\n"
     "- **Use when:** compressing an LLM and student/teacher drift hurts quality.\n"
     "- **Pros:** better student alignment to its own distribution.\n"
     "- **Gotchas:** extra sampling cost during training.",
     [(15, "knowledge-distillation")]),

    ("QLoRA", "proven", "fine-tuning,peft,lora,quantization",
     ["llm-fine-tuning-adaptation"],
     "**Fine-tune a 4-bit quantized base model with small LoRA adapters.**\n\n"
     "- **Use when:** adapting a large LLM on one GPU / a tight budget.\n"
     "- **Pros:** fits big models in little VRAM; often matches full fine-tuning.\n"
     "- **Gotchas:** occasionally a hair below full FT; merge/serve adapters carefully.",
     [(2, "llm-fine-tuning-adaptation")]),
]


def main():
    db = SessionLocal()
    now = datetime.utcnow()
    tasks = {t.slug: t for t in db.query(models.Task).all()}
    created = tagged = 0
    try:
        for name, maturity, tags, task_slugs, summary, insight_keys in TECHS:
            slug = slugify(name)
            tech = db.query(models.Technique).filter(models.Technique.slug == slug).first()
            if not tech:
                tech = models.Technique(name=name, slug=slug, summary=summary,
                                        maturity=maturity, tags=tags, last_reviewed_at=now)
                tech.tasks = [tasks[s] for s in task_slugs if s in tasks]
                db.add(tech); db.flush()
                log_change(db, "technique", tech.id, tech.name, "added",
                           "Technique from today's sources → " + ", ".join(task_slugs))
                created += 1
            for rid, tslug in insight_keys:
                task = tasks.get(tslug)
                if not task:
                    continue
                ins = db.query(models.Insight).filter_by(resource_id=rid, task_id=task.id).first()
                if ins and ins.technique_id is None:
                    ins.technique_id = tech.id
                    tagged += 1
        db.commit()
        print(f"Techniques created: {created} (total now {db.query(models.Technique).count()})")
        print(f"Insights tagged with a technique: {tagged}")
    except Exception as e:
        db.rollback(); print("ERROR:", e); raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
