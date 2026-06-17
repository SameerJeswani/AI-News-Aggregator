"""
Shared helpers for the AI Signal Desk dashboard.

Holds the design-token color map (kept in sync with assets/style.css),
the synthetic article dataset used until a real feed is wired in, and
small pure functions (time-ago formatting, filtering, stat rollups)
used by sidebar.py, cards.py, charts.py and dashboard.py.
"""

from __future__ import annotations

import random
from datetime import datetime, timedelta

import pandas as pd

# ---------------------------------------------------------------------------
# Design tokens (must mirror the CSS variables in assets/style.css)
# ---------------------------------------------------------------------------

CATEGORY_COLORS = {
    "Research": "#6C8EF5",
    "Industry": "#FF8A3D",
    "Funding": "#2DD4BF",
    "Policy": "#E85D75",
    "Open Source": "#B89BFF",
    "Product": "#F5C84C",
}

SENTIMENT_COLORS = {
    "Positive": "#2DD4BF",
    "Neutral": "#8B92A3",
    "Cautionary": "#E85D75",
}

CATEGORIES = list(CATEGORY_COLORS.keys())
SENTIMENTS = list(SENTIMENT_COLORS.keys())

SOURCES = [
    "The Signal Wire",
    "Compute Daily",
    "Frontier Brief",
    "Model Watch",
    "Stack Trace",
    "Deep Dive Weekly",
    "The Inference",
    "Byte Bulletin",
]

# Fictional companies/products so the demo data can never be mistaken for
# real reporting or attributed claims about real organizations.
COMPANIES = [
    "Helion AI", "Cortex Dynamics", "Nimbus Labs", "Vantage Systems",
    "Quanta Research", "Aether Intelligence", "Forge AI", "Lumen Labs",
    "Skyforge", "Halcyon Systems",
]

PRODUCTS = [
    "Atlas", "Pulsar", "Meridian", "Solace", "Vega", "Argon", "Quill", "Tessera",
]

HEADLINE_TEMPLATES = {
    "Research": [
        "{company} publishes benchmark showing {pct}% gain on long-context reasoning",
        "New paper from {company} questions scaling assumptions behind {product}",
        "{company} researchers open a dataset of {num}k annotated reasoning traces",
        "{company} claims state-of-the-art on multi-step planning tasks",
    ],
    "Industry": [
        "{company} restructures AI division ahead of {product} relaunch",
        "{company} signs multi-year compute deal to train {product}",
        "{company} and {company2} form joint venture on enterprise AI tooling",
        "{company} lays out roadmap for {product} through next year",
    ],
    "Funding": [
        "{company} raises ${amt}M Series {round_letter} to scale {product}",
        "{company} closes seed round led by undisclosed investors",
        "Valuation of {company} reportedly reaches ${val}B after new raise",
        "{company} secures credit facility to fund {product} compute cluster",
    ],
    "Policy": [
        "Regulators propose disclosure rules for frontier model training runs",
        "Draft legislation would require audits of {company}-style deployment systems",
        "Standards body releases voluntary safety framework for {product}-class models",
        "Lawmakers question {company} executives on {product} data sourcing",
    ],
    "Open Source": [
        "{company} open-sources {product} weights under permissive license",
        "Community fork of {product} adds support for on-device inference",
        "{company} releases evaluation harness used internally for {product}",
        "Open-source {product} variant surpasses prior community baseline",
    ],
    "Product": [
        "{company} ships {product} with native voice and tool-use support",
        "{company} brings {product} to enterprise customers via new API tier",
        "{company} unveils {product} update focused on coding workflows",
        "{company} adds memory feature to {product} consumer app",
    ],
}

SNIPPET_TEMPLATES = [
    "The release follows months of internal testing and a staged rollout to select partners.",
    "Details remain limited, but early access users report meaningful gains in reliability.",
    "The move signals a broader shift in how the company positions its AI roadmap.",
    "Analysts say the announcement raises fresh questions about compute costs at scale.",
    "The company says the change is part of a longer-term push toward general-purpose agents.",
    "Independent benchmarks have not yet confirmed the reported figures.",
    "The update is rolling out gradually and may not be visible to all users immediately.",
    "It's the second such announcement from the company this quarter.",
]


def _rand_headline(rng: random.Random, category: str) -> tuple[str, str]:
    template = rng.choice(HEADLINE_TEMPLATES[category])
    company, company2 = rng.sample(COMPANIES, 2)
    product = rng.choice(PRODUCTS)
    headline = template.format(
        company=company,
        company2=company2,
        product=product,
        pct=rng.randint(8, 47),
        num=rng.choice([12, 25, 60, 140, 300]),
        amt=rng.choice([18, 32, 60, 95, 140, 220]),
        val=rng.choice([1.2, 2.5, 4, 6.8, 9.5]),
        round_letter=rng.choice(["A", "B", "C", "D"]),
    )
    return headline, company


def generate_mock_articles(n: int = 140, days: int = 14, seed: int = 7) -> pd.DataFrame:
    """Build a deterministic synthetic dataset standing in for a live feed."""
    rng = random.Random(seed)
    now = datetime.now()
    rows = []
    for i in range(n):
        category = rng.choice(CATEGORIES)
        headline, company = _rand_headline(rng, category)
        published_at = now - timedelta(
            days=rng.uniform(0, days),
            hours=rng.uniform(0, 24),
        )
        sentiment = rng.choices(
            SENTIMENTS, weights=[0.45, 0.4, 0.15], k=1
        )[0]
        impact = round(rng.uniform(20, 99), 1)
        rows.append(
            {
                "id": i,
                "title": headline,
                "company": company,
                "category": category,
                "source": rng.choice(SOURCES),
                "sentiment": sentiment,
                "impact_score": impact,
                "summary": rng.choice(SNIPPET_TEMPLATES),
                "published_at": published_at,
                "url": "https://example.com/article/" + str(i),
            }
        )
    df = pd.DataFrame(rows).sort_values("published_at", ascending=False).reset_index(drop=True)
    return df


def time_ago(ts: datetime) -> str:
    """Human-readable relative time, e.g. '3h ago', '2d ago'."""
    delta = datetime.now() - ts
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    return f"{days}d ago"


def filter_articles(
    df: pd.DataFrame,
    categories: list[str] | None = None,
    sentiments: list[str] | None = None,
    sources: list[str] | None = None,
    days: int | None = None,
    query: str = "",
) -> pd.DataFrame:
    """Apply sidebar filter selections to the full dataset."""
    out = df.copy()
    if categories:
        out = out[out["category"].isin(categories)]
    if sentiments:
        out = out[out["sentiment"].isin(sentiments)]
    if sources:
        out = out[out["source"].isin(sources)]
    if days:
        cutoff = datetime.now() - timedelta(days=days)
        out = out[out["published_at"] >= cutoff]
    if query:
        q = query.lower().strip()
        out = out[
            out["title"].str.lower().str.contains(q)
            | out["company"].str.lower().str.contains(q)
            | out["summary"].str.lower().str.contains(q)
        ]
    return out.sort_values("published_at", ascending=False).reset_index(drop=True)


def compute_stats(df: pd.DataFrame, full_df: pd.DataFrame) -> dict:
    """Roll up headline metrics, with a simple period-over-period delta."""
    now = datetime.now()
    today_count = len(df[df["published_at"] >= now - timedelta(hours=24)])
    prev_count = len(
        full_df[
            (full_df["published_at"] < now - timedelta(hours=24))
            & (full_df["published_at"] >= now - timedelta(hours=48))
        ]
    )
    delta = today_count - prev_count

    active_sources = df["source"].nunique()

    if len(df):
        trending_category = df["category"].value_counts().idxmax()
        positive_share = round(
            100 * (df["sentiment"] == "Positive").sum() / len(df)
        )
    else:
        trending_category = "—"
        positive_share = 0

    return {
        "today_count": today_count,
        "today_delta": delta,
        "active_sources": active_sources,
        "trending_category": trending_category,
        "positive_share": positive_share,
        "total_filtered": len(df),
    }
