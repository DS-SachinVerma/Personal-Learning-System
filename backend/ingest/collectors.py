"""Source collectors. Each returns a list of normalized candidate dicts:

    {source, external_id, title, type, link, author, stars, raw, published_at, tags}

Every collector is defensive: a platform being down/rate-limited logs a warning
and returns [], so one bad source never kills the run.
"""
import re
import time
from datetime import datetime, timezone

import requests
import feedparser

from . import config

_S = requests.Session()
_S.headers.update({"User-Agent": config.USER_AGENT})


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def _warn(source, err):
    print(f"  ! {source}: {type(err).__name__}: {err}")


def _get_json(url, params=None, headers=None):
    r = _S.get(url, params=params, headers=headers, timeout=config.TIMEOUT)
    r.raise_for_status()
    return r.json()


def _get_feed(url, params=None):
    """Fetch via requests (follows http->https redirects, sets UA) then parse.
    feedparser's own fetcher doesn't follow redirects reliably."""
    r = _S.get(url, params=params, timeout=config.TIMEOUT)
    r.raise_for_status()
    return feedparser.parse(r.content)


def _from_struct(st):
    if not st:
        return None
    try:
        return datetime.fromtimestamp(time.mktime(st), tz=timezone.utc).replace(tzinfo=None)
    except Exception:
        return None


def _from_iso(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        return None


def _clean_arxiv_id(raw_id):
    """Normalize any arXiv reference to a bare, version-less id (e.g. 2401.01234)."""
    if not raw_id:
        return None
    m = re.search(r"(\d{4}\.\d{4,5})", raw_id)
    if m:
        return m.group(1)
    # old-style ids like cs/0112017
    m = re.search(r"([a-z\-]+/\d{7})", raw_id)
    return m.group(1) if m else None


def _is_relevant(text):
    t = (text or "").lower()
    return any(k in t for k in config.ML_KEYWORDS)


def _paper(arxiv_id, title, author, raw, link, published_at, via):
    """Uniform paper candidate — keyed by arXiv id so the same paper found on
    several platforms dedups to one row. The platform that surfaced it is a tag."""
    return {
        "source": "arxiv", "external_id": arxiv_id, "type": "paper",
        "title": title, "author": author, "stars": None, "raw": raw,
        "link": link or f"https://arxiv.org/abs/{arxiv_id}",
        "published_at": published_at, "tags": f"via:{via}",
    }


# --------------------------------------------------------------------------
# research
# --------------------------------------------------------------------------

def collect_arxiv(categories=None, limit=config.DEFAULT_LIMIT, query=None):
    # topical search (all:<query>) when a query is given, else sweep categories by recency
    if query:
        q, sort = f"all:{query}", "relevance"
    else:
        categories = categories or config.ARXIV_CATEGORIES
        q, sort = " OR ".join(f"cat:{c}" for c in categories), "submittedDate"
    out = []
    try:
        feed = _get_feed(
            "https://export.arxiv.org/api/query",
            params={"search_query": q, "sortBy": sort,
                    "sortOrder": "descending", "max_results": limit},
        )
        for e in feed.entries:
            aid = _clean_arxiv_id(e.get("id"))
            if not aid:
                continue
            authors = ", ".join(a.get("name", "") for a in e.get("authors", [])[:3])
            if len(e.get("authors", [])) > 3:
                authors += " et al."
            out.append(_paper(
                aid, e.get("title", "").strip().replace("\n", " "),
                authors, (e.get("summary", "") or "").strip(),
                e.get("link"), _from_struct(e.get("published_parsed")), "arxiv",
            ))
    except Exception as err:
        _warn("arxiv", err)
    return out


def collect_hf_papers(limit=config.DEFAULT_LIMIT):
    out = []
    try:
        data = _get_json("https://huggingface.co/api/daily_papers", params={"limit": limit})
        for item in data:
            p = item.get("paper", item)
            aid = _clean_arxiv_id(p.get("id") or p.get("arxivId"))
            if not aid:
                continue
            authors = ", ".join(a.get("name", "") for a in (p.get("authors") or [])[:3]) or None
            out.append(_paper(
                aid, p.get("title", "").strip(), authors,
                (p.get("summary") or "").strip(),
                f"https://huggingface.co/papers/{aid}", _from_iso(p.get("publishedAt")), "hf-papers",
            ))
    except Exception as err:
        _warn("hf-papers", err)
    return out


def collect_semantic_scholar(queries=None, limit=config.DEFAULT_LIMIT):
    queries = queries or config.SEMANTIC_SCHOLAR_QUERIES
    out = []
    for query in queries:
        try:
            data = _get_json(
                "https://api.semanticscholar.org/graph/v1/paper/search",
                params={"query": query, "limit": limit,
                        "fields": "title,abstract,authors,externalIds,url,year"},
            )
            for p in data.get("data", []):
                ext = p.get("externalIds") or {}
                aid = _clean_arxiv_id(ext.get("ArXiv"))
                if not aid:
                    continue  # keep the arXiv-keyed dedup simple; skip non-arXiv papers
                authors = ", ".join(a.get("name", "") for a in (p.get("authors") or [])[:3]) or None
                out.append(_paper(
                    aid, p.get("title", ""), authors, (p.get("abstract") or "").strip(),
                    p.get("url"), None, "semantic-scholar",
                ))
        except Exception as err:
            _warn("semantic-scholar", err)
    return out


def collect_paperswithcode(limit=config.DEFAULT_LIMIT):
    out = []
    try:
        data = _get_json("https://paperswithcode.com/api/v1/papers/", params={"items_per_page": limit})
        for p in data.get("results", []):
            aid = _clean_arxiv_id(p.get("arxiv_id"))
            if not aid:
                continue
            out.append(_paper(
                aid, p.get("title", ""), p.get("authors") and ", ".join(p["authors"][:3]) or None,
                (p.get("abstract") or "").strip(), p.get("url_abs"),
                _from_iso(p.get("published")), "paperswithcode",
            ))
    except Exception as err:
        _warn("paperswithcode", err)
    return out


# --------------------------------------------------------------------------
# packages / models
# --------------------------------------------------------------------------

def collect_github(queries=None, limit=config.DEFAULT_LIMIT, token=None, since_days=30):
    from datetime import timedelta
    queries = queries or config.GITHUB_QUERIES
    since = (datetime.utcnow() - timedelta(days=since_days)).strftime("%Y-%m-%d")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    out = []
    for query in queries:
        try:
            data = _get_json(
                "https://api.github.com/search/repositories",
                params={"q": f"{query} created:>={since}", "sort": "stars",
                        "order": "desc", "per_page": limit},
                headers=headers,
            )
            for r in data.get("items", []):
                out.append({
                    "source": "github", "external_id": r["full_name"], "type": "repo",
                    "title": r["full_name"], "author": r["owner"]["login"],
                    "stars": r.get("stargazers_count"), "raw": r.get("description") or "",
                    "link": r["html_url"], "published_at": _from_iso(r.get("created_at")),
                    "tags": ",".join(r.get("topics", [])[:6]),
                })
        except Exception as err:
            _warn("github", err)
    return out


def _collect_hf(kind, sort, limit, type_, search=None):
    out = []
    try:
        params = {"sort": sort, "direction": -1, "limit": limit}
        if search:
            params["search"] = search
        data = _get_json(f"https://huggingface.co/api/{kind}", params=params)
        for m in data:
            mid = m.get("id") or m.get("modelId")
            if not mid:
                continue
            tags = [t for t in (m.get("tags") or []) if ":" not in t][:6]
            out.append({
                "source": "huggingface", "external_id": mid, "type": type_,
                "title": mid, "author": mid.split("/")[0] if "/" in mid else None,
                "stars": m.get("likes"),
                "raw": (m.get("pipeline_tag") or "") + " " + " ".join(tags),
                "link": f"https://huggingface.co/{'datasets/' if kind == 'datasets' else ''}{mid}",
                "published_at": _from_iso(m.get("createdAt")), "tags": ",".join(tags),
            })
    except Exception as err:
        _warn(f"hf-{kind}", err)
    return out


def collect_hf_models(limit=config.DEFAULT_LIMIT, search=None):
    sort = "downloads" if search else config.HF_MODELS_SORT  # trending is meaningless within a search
    return _collect_hf("models", sort, limit, "model", search=search)


def collect_hf_datasets(limit=config.DEFAULT_LIMIT, search=None):
    sort = "downloads" if search else config.HF_DATASETS_SORT
    return _collect_hf("datasets", sort, limit, "dataset", search=search)


def collect_pypi(limit=config.DEFAULT_LIMIT):
    """Best-effort: newest PyPI releases filtered to ML-relevant ones."""
    out = []
    try:
        feed = _get_feed("https://pypi.org/rss/updates.xml")
        for e in feed.entries:
            if len(out) >= limit:
                break
            if not _is_relevant(f"{e.get('title','')} {e.get('summary','')}"):
                continue
            name = (e.get("title", "").split(" ") or [""])[0]
            out.append({
                "source": "pypi", "external_id": name, "type": "package",
                "title": e.get("title", ""), "author": None, "stars": None,
                "raw": e.get("summary", ""), "link": e.get("link"),
                "published_at": _from_struct(e.get("published_parsed")), "tags": "",
            })
    except Exception as err:
        _warn("pypi", err)
    return out


# --------------------------------------------------------------------------
# blogs (anywhere)
# --------------------------------------------------------------------------

def collect_blogs(feeds=None, per_feed=5):
    feeds = feeds or config.BLOG_FEEDS
    out = []
    for url in feeds:
        try:
            feed = _get_feed(url)
            site = feed.feed.get("title", url)
            taken = 0
            for e in feed.entries:
                if taken >= per_feed:
                    break
                text = f"{e.get('title','')} {e.get('summary','')}"
                if not _is_relevant(text):
                    continue
                out.append({
                    "source": "blog", "external_id": (e.get("id") or e.get("link") or "").strip(),
                    "type": "blog", "title": e.get("title", "").strip(),
                    "author": e.get("author") or site, "stars": None,
                    "raw": re.sub(r"<[^>]+>", "", e.get("summary", ""))[:1000],
                    "link": e.get("link"),
                    "published_at": _from_struct(e.get("published_parsed")), "tags": "",
                })
                taken += 1
        except Exception as err:
            _warn(f"blog:{url}", err)
    return out


# registry: name -> (callable, needs a per-source limit?)
COLLECTORS = {
    "arxiv": collect_arxiv,
    "hf-papers": collect_hf_papers,
    "semantic-scholar": collect_semantic_scholar,
    "paperswithcode": collect_paperswithcode,
    "github": collect_github,
    "hf-models": collect_hf_models,
    "hf-datasets": collect_hf_datasets,
    "pypi": collect_pypi,
    "blogs": collect_blogs,
}

# a sensible default set that won't flood intake
DEFAULT_SOURCES = ["arxiv", "hf-papers", "github", "hf-models", "blogs"]
