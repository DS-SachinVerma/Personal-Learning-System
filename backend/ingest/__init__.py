"""Pluggable ingestion: collect raw candidates from many platforms into intake.

The script only COLLECTS. Curation (summaries, insights, linking to tasks) is
done afterwards. Every collector returns a list of normalized candidate dicts;
the runner upserts them via the (source, external_id) dedup key so nothing is
inserted twice.
"""
