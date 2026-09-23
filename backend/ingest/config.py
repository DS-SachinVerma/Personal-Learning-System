"""Ingestion configuration — edit freely; nothing here is fixed.

Papers and packages come from specific platforms (stable ids → clean dedup);
blogs can come from anywhere, so BLOG_FEEDS is just a starting list you extend.
"""

# --- research: arXiv categories to sweep (https://arxiv.org/category_taxonomy) ---
ARXIV_CATEGORIES = ["cs.LG", "cs.CL", "cs.CV", "cs.AI", "stat.ML"]

# --- packages: GitHub search. Repos created recently, ranked by stars. ---
# Each query is run separately; keep them broad-but-relevant.
GITHUB_QUERIES = [
    "machine learning", "large language model", "llm", "rag retrieval",
    "diffusion model", "time series forecasting", "computer vision",
]

# --- Hugging Face Hub: how to rank models/datasets ---
HF_MODELS_SORT = "trendingScore"   # or "likes7d", "downloads"
HF_DATASETS_SORT = "trendingScore"

# --- Semantic Scholar / Papers with Code search seeds ---
SEMANTIC_SCHOLAR_QUERIES = ["large language models", "retrieval augmented generation"]

# --- blogs: RSS/Atom feeds. Add any URL — company blogs, Substacks, etc. ---
BLOG_FEEDS = [
    "https://huggingface.co/blog/feed.xml",
    "https://bair.berkeley.edu/blog/feed.xml",
    "https://blog.google/technology/ai/rss/",
    "https://openai.com/news/rss.xml",
    "https://distill.pub/rss.xml",
    "https://eugeneyan.com/rss/",
    "https://lilianweng.github.io/index.xml",
]

# Keyword gate for generic feeds (blogs) so we don't ingest non-ML posts.
# Papers/repos/models are already ML-scoped by their platform, so they skip this.
ML_KEYWORDS = [
    "machine learning", "deep learning", "neural", "llm", "language model",
    "transformer", "rag", "retrieval", "embedding", "diffusion", "agent",
    "fine-tun", "quantiz", "inference", "gpt", "vision", "segmentation",
    "forecast", "recommend", "reinforcement", "gradient", "dataset", "benchmark",
    "vector", "prompt", "multimodal", "clip", "ml", "ai model",
]

# Per-source default cap, so a run never floods intake.
DEFAULT_LIMIT = 10

# Networking
USER_AGENT = "TechniqueLibrary-Ingest/1.0 (personal learning system)"
TIMEOUT = 25
