#!/usr/bin/env python3
"""Daily collector — fills the intake queue from many platforms.

It only COLLECTS raw candidates (status='intake'); curation happens after.
Dedup is by (source, external_id): a re-seen item refreshes its stars/last_seen
instead of inserting a copy.

Examples:
    python collect.py                         # default sources, 10 items each
    python collect.py --sources arxiv,github --limit 15
    python collect.py --sources blogs --blog-feed https://some.blog/rss.xml
    python collect.py --list                  # show available sources
    python collect.py --dry-run               # collect + print, write nothing

GitHub allows only 60 search calls/hour unauthenticated; set GITHUB_TOKEN to raise it.
"""
import sys, os, argparse
from datetime import datetime

try:  # Windows consoles default to cp1252 and choke on arrows/bullets
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app import models
from app.deps import log_change
from ingest import collectors, config

models.Base.metadata.create_all(bind=engine)


def gather(sources, limit, extra_feeds, gh_token, query=None):
    """Run each selected collector with the right arguments. When `query` is
    given, the topical collectors target it instead of sweeping by recency."""
    dispatch = {
        "arxiv": lambda: collectors.collect_arxiv(limit=limit, query=query),
        "hf-papers": lambda: collectors.collect_hf_papers(limit=limit),
        "semantic-scholar": lambda: collectors.collect_semantic_scholar(
            queries=[query] if query else None, limit=limit),
        "paperswithcode": lambda: collectors.collect_paperswithcode(limit=limit),
        "github": lambda: collectors.collect_github(
            queries=[query] if query else None, limit=limit, token=gh_token,
            since_days=3650 if query else 30),
        "hf-models": lambda: collectors.collect_hf_models(limit=limit, search=query),
        "hf-datasets": lambda: collectors.collect_hf_datasets(limit=limit, search=query),
        "pypi": lambda: collectors.collect_pypi(limit=limit),
        "blogs": lambda: collectors.collect_blogs(
            feeds=(config.BLOG_FEEDS + extra_feeds) if extra_feeds else None,
            per_feed=max(2, limit // 4),
        ),
    }
    results = {}
    for s in sources:
        fn = dispatch.get(s)
        if not fn:
            print(f"  ? unknown source '{s}' — skipping")
            continue
        print(f"→ collecting {s} …")
        results[s] = fn()
        print(f"  got {len(results[s])} candidate(s)")
    return results


def upsert(db, cand):
    """Return 'new' | 'refreshed' | 'skip'."""
    ext = (cand.get("external_id") or "").strip()
    if not ext or not cand.get("title"):
        return "skip"
    existing = (
        db.query(models.Resource)
        .filter(models.Resource.source == cand["source"], models.Resource.external_id == ext)
        .first()
    )
    if existing:
        existing.last_seen_at = datetime.utcnow()
        if cand.get("stars") is not None:
            existing.stars = cand["stars"]
        return "refreshed"
    r = models.Resource(
        title=cand["title"][:500], type=cand.get("type"), link=cand.get("link"),
        summary=None, tags=cand.get("tags"), status="intake", source=cand["source"],
        external_id=ext, author=(cand.get("author") or None), stars=cand.get("stars"),
        raw=cand.get("raw"), published_at=cand.get("published_at"),
        last_seen_at=datetime.utcnow(),
    )
    db.add(r)
    db.flush()
    log_change(db, "resource", r.id, r.title, "added", f"Collected from {r.source} ({r.type})")
    return "new"


def main():
    ap = argparse.ArgumentParser(description="Collect raw candidates into intake.")
    ap.add_argument("--sources", default=",".join(collectors.DEFAULT_SOURCES),
                    help="comma list; see --list")
    ap.add_argument("--limit", type=int, default=config.DEFAULT_LIMIT, help="per-source cap")
    ap.add_argument("--query", default=None,
                    help="topical search (e.g. 'OCR') for arxiv/github/hf-models/semantic-scholar")
    ap.add_argument("--blog-feed", action="append", default=[], help="extra RSS feed (repeatable)")
    ap.add_argument("--dry-run", action="store_true", help="collect + print, write nothing")
    ap.add_argument("--list", action="store_true", help="list sources and exit")
    args = ap.parse_args()

    if args.list:
        print("Available sources:")
        for name in collectors.COLLECTORS:
            mark = " (default)" if name in collectors.DEFAULT_SOURCES else ""
            print(f"  - {name}{mark}")
        return

    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    gh_token = os.environ.get("GITHUB_TOKEN")
    if args.query:
        print(f"Topical search: '{args.query}'")
    results = gather(sources, args.limit, args.blog_feed, gh_token, query=args.query)

    db = SessionLocal()
    summary = {}
    new_titles = []
    try:
        for source, cands in results.items():
            counts = {"new": 0, "refreshed": 0, "skip": 0}
            for c in cands:
                status = "new" if args.dry_run else upsert(db, c)
                if args.dry_run:
                    # still detect would-be dupes for an honest preview
                    ext = (c.get("external_id") or "").strip()
                    exists = ext and db.query(models.Resource).filter(
                        models.Resource.source == c["source"],
                        models.Resource.external_id == ext).first()
                    status = "refreshed" if exists else ("skip" if not ext else "new")
                counts[status] += 1
                if status == "new":
                    new_titles.append((source, c.get("title", "")))
            summary[source] = counts
        if not args.dry_run:
            db.commit()
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()

    print("\n" + "=" * 56)
    print("COLLECTION SUMMARY" + ("  (dry run — nothing written)" if args.dry_run else ""))
    print("=" * 56)
    total_new = 0
    for source, c in summary.items():
        total_new += c["new"]
        print(f"  {source:<18} new {c['new']:<3} refreshed {c['refreshed']:<3} skipped {c['skip']}")
    print(f"\n  {total_new} new item(s) landed in intake.")
    if new_titles:
        print("  New:")
        for source, title in new_titles[:40]:
            print(f"   • [{source}] {title[:80]}")
    print("\nNext: open Intake in the app, or ask Claude to curate today's intake.")


if __name__ == "__main__":
    main()
