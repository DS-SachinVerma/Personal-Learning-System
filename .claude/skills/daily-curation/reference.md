# Curation reference — fields, recipes, commands

## Field reference (what goes where)

**Task** — a kind of job. `POST /tasks/`
- `name`, `domain` (top-level bucket), `one_liner` (when to reach for it), `overview` (markdown, optional), `tags`.
- Links: `technique_ids[]`. Slug auto-generated & unique.

**Technique** — a named method. `POST /techniques/`
- `name`, `summary` (markdown: **what it is / use when / pros / gotchas**), `maturity` (proven|emerging|experimental|legacy), `tags`, `task_ids[]`.
- Creating with an existing slug **links to the existing technique** instead of duplicating.

**Resource** — a source. Created by the collector as `intake`; you curate it.
- `title`, `type` (paper|repo|model|dataset|blog|docs|video|package), `link`, `summary` (markdown — the study layer), `tags`, `status` (intake|reviewed|archived), `source`, `external_id`, `author`, `stars`, `raw` (original abstract), `published_at`.
- `PUT /resources/{id}` to set `summary`, `status`, `tags`, `last_reviewed_at`.

**Insight** — the takeaway + the link. `POST /insights/`
- `resource_id` (required), one or both of `task_id` / `technique_id`, `title` (short), `detail` (markdown), `kind` (`use`|`study`, default `use`).
- Creating an insight auto-flips the resource to `reviewed`.

**ResourceVersion** — a version-history entry. `POST /resources/{id}/versions`
- `version_label` ("v3.0" / a date), `changed_on`, `what_changed`, `why_it_matters`, `link`.

**Experiment** — a benchmark for a task. `POST /experiments/`
- `title`, `task_id`, `dataset`, `metric`, `results` (markdown table), `code_link`.

## Recipes

**A repo/model that's a tool for a task**
1. `PUT /resources/{id}` → `summary`, `status='reviewed'`.
2. `POST /insights/` → `{resource_id, task_id, kind:'use', title, detail}` (one per task it serves).
3. If it implements a named method with no technique yet: `POST /techniques/` → link `task_ids`, then set that insight's `technique_id`.

**A paper/tutorial that's theory (study)**
1. `PUT /resources/{id}` → `summary`, `status='reviewed'`.
2. `POST /insights/` → `{resource_id, task_id, kind:'study', title:'Further reading', detail}` (skip task_id if no single home — it still shows in the Reading list).

**A new method/approach**
1. `POST /techniques/` → `{name, summary, maturity, tags, task_ids:[...]}`.
2. Point the evidencing insight(s) at it via `technique_id`.

**An update to something we already have**
1. Find the existing resource (`GET /resources/?q=...` or by `external_id`).
2. `POST /resources/{id}/versions` → what changed + why it matters. Do **not** create a new resource.

**Noise** → `PUT /resources/{id}` → `status='archived'`. Nothing else.

## Batch curation via a script (efficient for a day's intake)

For a whole batch, a Python script using the ORM is fastest — pattern used before lives in
`backend/curate_intake.py`, `backend/tie_study_to_tasks.py`, `backend/add_techniques.py` (keep them
as worked examples). **Make batch scripts idempotent**: before inserting an insight/technique,
check it doesn't already exist (`filter_by(resource_id=..., task_id=...)` / slug lookup), or a
re-run duplicates rows. Always `sys.stdout.reconfigure(encoding='utf-8')` at the top.

Skeleton:
```python
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app.database import SessionLocal
from app import models
from app.deps import slugify, log_change
db = SessionLocal()
tasks = {t.slug: t for t in db.query(models.Task).all()}
r = db.query(models.Resource).get(RID)
r.summary = "..."; r.status = "reviewed"
if not db.query(models.Insight).filter_by(resource_id=r.id, task_id=tasks['SLUG'].id).first():
    db.add(models.Insight(resource_id=r.id, task_id=tasks['SLUG'].id, kind='use',
                          title='...', detail='...'))
db.commit()
```

## Rich resource summaries (subagent per resource)

Resource summaries must be **substantial and grounded in the real source** — not one-line
paraphrases of the collected `raw`. So **spawn one summarizer subagent per kept resource**.

**Per-agent contract.** Give the agent the resource's `id`, `title`, `link`, `type`, `source`,
and `raw`. Instruct it to:
1. **Fetch the actual source** with WebFetch (the repo README / paper abstract page / blog post) —
   summarize from what it reads, never from the title alone. If the fetch fails, say so and summarize
   from `raw` only, flagging it as unverified.
2. Write a markdown summary to **this exact template** (~150–250 words, no fluff):
   ```
   **<one line: what it is + its niche>**

   **What it is** — 2–3 sentences of substance.
   **How it works / key ideas** — 2–4 bullets.
   **Where we'd use it** — 2–3 concrete data-science / office use cases.
   **Strengths** — bullets.
   **Caveats** — bullets.
   **Maturity / adoption** — one line (stars, lab, recency, who uses it).
   ```
3. **Save (do NOT write to the DB)** to `<scratchpad>/res_summaries/res_<id>.json` as
   `{"id": <id>, "summary": "<markdown>"}`. Return one line: the id + a 6-word gist.

Run the agents in the background, in batches. When they finish, apply all at once (one DB writer,
no SQLite lock contention):
```
cd backend && ../venv/Scripts/python.exe apply_summaries.py --dir <scratchpad>/res_summaries
```
Scope: summarize the **reviewed** resources (the ones with insights — what the user reads).
Archived/noise resources don't need rich summaries. `type in (paper,repo,model,dataset,blog)`.

## Sources (edit freely — nothing is fixed)
Config: `backend/ingest/config.py`. Collectors: `backend/ingest/collectors.py`.
- **Research** (keyed by arXiv id): `arxiv`, `hf-papers`, `semantic-scholar`, `paperswithcode`.
- **Packages/models**: `github`, `hf-models`, `hf-datasets`, `pypi`.
- **Blogs** (any RSS): `blogs` — add feeds to `BLOG_FEEDS`, or `--blog-feed URL` for a one-off.
- Add a new source = add a collector fn returning normalized dicts + register it in
  `collectors.COLLECTORS` and the `dispatch` map in `collect.py`.
- `ML_KEYWORDS` gates generic blog feeds; papers/repos/models are pre-scoped by platform.

## Command cheat-sheet
```
# backend API (needed for the app + curl curation)
cd backend && ../venv/Scripts/python.exe -m uvicorn app.main:app --port 8000

# frontend (read surface) — opens on http://localhost:5176  (Vite binds localhost, not 127.0.0.1)
cd frontend && npm run dev

# collect today's candidates
cd backend && ../venv/Scripts/python.exe collect.py --limit 10

# topical search ("look for X") — github/arxiv/hf-models/semantic-scholar
cd backend && ../venv/Scripts/python.exe collect.py --sources github,arxiv,hf-models,semantic-scholar --query "OCR" --limit 8

# reseed the taxonomy (idempotent; only adds missing tasks)
cd backend && ../venv/Scripts/python.exe seed_taxonomy.py
```

## Gotchas
- **UTF-8**: reading JSON through `curl | python` on Windows shows mojibake (`â€"` for `—`) because
  stdin defaults to cp1252. The DB/API/browser are correct — reconfigure stdin to debug.
- **GitHub rate limit**: 60 search calls/hr unauthenticated → set `GITHUB_TOKEN`.
- **DB location**: `sqlite:///./learning_tracker.db` is relative to CWD — always run scripts and the
  server **from `backend/`** so they share `backend/learning_tracker.db`. Old backups: `*.db.bak-*`.
- **Schema changes** need the server restarted (uvicorn `--reload` doesn't always catch them), and a
  new column on an existing table needs a manual `ALTER TABLE` (create_all won't alter).
