---
name: daily-curation
description: Run the daily ML technique-library curation — collect fresh papers/repos/models/blogs into intake, then triage each into tasks/techniques as actionable or study, and hand back a digest. Use whenever the user says "daily curation", "collect today", "curate intake", "run the collector", "what's new today", or starts the daily learning-system routine.
---

# Daily curation

This repo is an **ML technique reference library**, not a study list. Its job: when a task
lands on the user's desk at work, they open the matching **task page** and instantly see the
candidate techniques, the sources behind them, and any benchmarks. Curation is what keeps that
shelf trustworthy. **Claude does the curation; the user just reads the digest.**

Read the memory files first for context: `[[technique-library-architecture]]` and
`[[learning-system-remaining-work]]`.

## The four layers (what goes where)

| Layer | Means | Example |
|---|---|---|
| **Task** | a *kind of job* you get assigned | "Semantic Search / RAG" |
| **Technique** | a named *method* for doing tasks | "Hybrid Retrieval (BM25 + Vector)" |
| **Resource** | a concrete *source*: paper / repo / model / dataset / blog | the loci repo |
| **Insight** | the *takeaway* a resource gives for a task/technique — **and the link** | "hybrid retrieval in ~300 lines" |

An **Insight** carries a `kind`:
- **`use`** → actionable. Shows on the task's *"What our sources say"* shelf.
- **`study`** → background. Shows under the task's *"Further reading"* lane and in the Reading list.

One resource → many insights → many tasks. A resource can serve several tasks with a *different*
takeaway for each. Overlaps live in the links, never in copied rows.

## The daily routine

### 1. Collect (fills intake)
```
cd backend
../venv/Scripts/python.exe collect.py --limit 10          # default sources
../venv/Scripts/python.exe collect.py --list              # all sources
../venv/Scripts/python.exe collect.py --sources arxiv,github --blog-feed https://any.blog/rss

# TOPICAL search — use when the user says "look for X" (e.g. OCR, anomaly detection):
../venv/Scripts/python.exe collect.py --sources github,arxiv,hf-models,semantic-scholar --query "OCR document" --limit 8
```
`--query` targets a topic across github/arxiv/hf-models/semantic-scholar (github drops its
recency filter so established repos surface). The script **only collects** raw candidates into `status='intake'`. It dedups on
`(source, external_id)` — a re-seen item refreshes stars/last_seen, never duplicates.
Set `GITHUB_TOKEN` env to lift GitHub's 60/hr limit. GitHub is the noisiest source (many
default queries) — lower `--limit` or trim `GITHUB_QUERIES` in `ingest/config.py` if intake floods.

### 2. Read intake
```
curl -s "http://127.0.0.1:8000/resources/?status=intake"
```
Each item has `title`, `type`, `source`, `link`, and `raw` (the abstract/description the script
grabbed). **On Windows, reading JSON via `curl | python` corrupts UTF-8** unless you reconfigure
stdin: `sys.stdin=io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')`. The stored data is fine —
it's only a console display artifact.

### 3. Triage every item into one of three fates
- **Actionable** ("we could use this at the office") → keep, write summary, add `use` insight(s) to task(s), extract a technique if there's a named method, set `status='reviewed'`.
- **Study** (theory, tutorials, frontier papers — good to understand, not job-ready) → keep, write summary, add a `study` insight tied to the relevant task (or leave untied if no single home), `status='reviewed'`.
- **Noise** (marketing, PR, vague personal repos, off-topic) → `status='archived'`. Don't force it anywhere.

### 4. Curate the keepers (see rules below and `reference.md` for exact fields/recipes)
For each kept resource:
1. **Write a rich summary — one summarizer subagent per resource.** Do NOT write thin one-liners
   yourself. Spawn a subagent per kept resource that fetches the actual source and writes a
   structured summary to the template. Collect them, then apply in one pass. Full contract +
   template + commands in `reference.md` → **"Rich resource summaries (subagent per resource)"**.
2. Decide the **task(s)** it touches. For each, create an **insight** with `kind` set correctly.
   (Insight `detail` is the short per-task takeaway; the rich *summary* lives on the resource.)
3. Ask: *is there a named method here worth its own **technique** page?* If yes, create/link it
   and tag the evidencing insight with the `technique_id`.
4. If it's an **update to a resource we already have**, add a **version-history** entry instead of a new row.
5. Flip `status` to `reviewed` (or `archived`).

### 5. Hand back the digest
Report **"what we added/changed today"**, grouped like the template below. Source of truth:
`GET /digest/?days=1`. Keep it scannable — the user reads only this.

```
📅 Daily digest — <date>
Collected N candidates → X filed to tasks · Y to Reading list · Z archived.

🎯 Filed to tasks (actionable)
  <Task>: <source> — <takeaway>
🧩 Techniques added
  <Technique> [maturity] → <task>  (from <source>)
📖 To Reading list (study)
  <title> → <task>
🗑️ Archived (Z): <one-line why>
```

## Decision rules (the ones that keep the library honest)

- **Study never touches the actionable shelf.** Study value → resource summary (+ a `study` insight, and the technique summary if it explains a method). Only "use at the office" takeaways become `use` insights. This is the single most important rule.
- **Create a technique when there's a reusable named method** (a way to retrieve, quantize, fine-tune, chunk…), not for every source. A tool that just *implements* a technique → a `use` insight pointing at the existing technique, not a new one.
- **Dedup by concept, not just by id.** Techniques/tasks are unique by `slug` — before creating "embeddings" again, link to the existing one. Near-duplicate sources that aren't caught by `external_id` are a judgment call: link to the existing technique or flag it in the digest.
- **Papers are keyed by arXiv id** (`source='arxiv'`) no matter which platform surfaced them, so the same paper from arXiv + HF Papers + Semantic Scholar collapses to one row; the platform becomes a `via:` tag.
- **Updates are version-history events**, not overwrites. New release / new paper version / breaking change → a `ResourceVersion` (what changed + *why it matters to us*).
- **Tasks and techniques evolve.** If a genuinely new kind of job or method appears that no task/domain covers, create a new task (pick or add a domain) — don't jam it into a poor fit.
- **Maturity labels:** `proven` = industry-standard or we've used it; `emerging` = strong, not yet proven for us; `experimental` = new/research; `legacy` = superseded. (Confirm the user's preferred standard if unsure.)

## Reference
Field-by-field "what goes where", the API/DB write recipes, the source list, and command
cheat-sheet are in `reference.md` (same folder). Read it before writing to the system.
