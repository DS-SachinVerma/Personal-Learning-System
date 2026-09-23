#!/usr/bin/env python3
"""Apply rich summaries produced by the per-resource summarizer subagents.

Each subagent writes one JSON file: {"id": <resource_id>, "summary": "<markdown>"}.
This reads them all and updates resources.summary in a single transaction, so the
concurrent agents never touch the DB (no SQLite lock contention).

    python apply_summaries.py --dir <folder-of-json-files>
"""
import sys, os, json, glob, argparse
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app import models
from app.deps import log_change


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="folder of res_<id>.json files")
    args = ap.parse_args()

    files = glob.glob(os.path.join(args.dir, "*.json"))
    db = SessionLocal()
    n = miss = 0
    try:
        for f in files:
            try:
                data = json.load(open(f, encoding="utf-8"))
            except Exception as e:
                print(f"  ! bad json {f}: {e}"); continue
            rid, summary = data.get("id"), (data.get("summary") or "").strip()
            if not rid or not summary:
                continue
            r = db.query(models.Resource).get(rid)
            if not r:
                miss += 1; continue
            r.summary = summary
            log_change(db, "resource", r.id, r.title, "updated", "Rich summary written")
            n += 1
        db.commit()
        print(f"Applied {n} summaries ({miss} missing resources, {len(files)} files).")
    except Exception as e:
        db.rollback(); print("ERROR:", e); raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
