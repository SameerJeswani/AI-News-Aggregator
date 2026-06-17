"""Metric cards and news-feed cards for the Signal Desk."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app.ui.utils import CATEGORY_COLORS, SENTIMENT_COLORS, time_ago


def render_metric_cards(stats: dict) -> None:
    """Render the top row of KPI cards."""
    cols = st.columns(4)

    delta = stats["today_delta"]
    if delta > 0:
        delta_cls, delta_text = "up", f"▲ {delta} vs prior 24h"
    elif delta < 0:
        delta_cls, delta_text = "down", f"▼ {abs(delta)} vs prior 24h"
    else:
        delta_cls, delta_text = "flat", "— flat vs prior 24h"

    cards = [
        ("Articles · 24h", str(stats["today_count"]), delta_text, delta_cls),
        ("Active Sources", str(stats["active_sources"]), "tracked in view", "flat"),
        ("Trending Category", stats["trending_category"], "by volume", "flat"),
        ("Positive Sentiment", f"{stats['positive_share']}%", "of filtered set", "flat"),
    ]

    for col, (label, value, sub, cls) in zip(cols, cards):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-card__label">{label}</div>
                    <div class="metric-card__value">{value}</div>
                    <div class="metric-card__sub {cls}">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _news_card_html(row: pd.Series) -> str:
    cat_color = CATEGORY_COLORS.get(row["category"], "#FF8A3D")
    sent_color = SENTIMENT_COLORS.get(row["sentiment"], "#8B92A3")
    return f"""
    <div class="news-card" style="--cat-color:{cat_color};">
        <div class="news-card__meta">
            <span class="news-card__tag" style="--cat-color:{cat_color};">{row['category']}</span>
            <span>{row['source']}</span>
            <span>·</span>
            <span>{time_ago(row['published_at'])}</span>
            <span class="news-card__sentiment" style="--sent-color:{sent_color};" title="{row['sentiment']}"></span>
        </div>
        <p class="news-card__title">{row['title']}</p>
        <p class="news-card__summary">{row['summary']}</p>
        <div class="news-card__footer">
            <span class="news-card__impact">IMPACT {row['impact_score']:.0f}</span>
            <a class="news-card__link" href="{row['url']}" target="_blank">Read source ↗</a>
        </div>
    </div>
    """


def render_news_feed(df: pd.DataFrame, page_size: int = 12) -> None:
    """Render the article list with a simple 'load more' pagination."""
    if df.empty:
        st.markdown(
            '<div class="empty-state">No signals match these filters. '
            "Try widening the timeframe or clearing a filter.</div>",
            unsafe_allow_html=True,
        )
        return

    if "feed_limit" not in st.session_state:
        st.session_state["feed_limit"] = page_size

    visible = df.iloc[: st.session_state["feed_limit"]]
    html = "".join(_news_card_html(row) for _, row in visible.iterrows())
    st.markdown(html, unsafe_allow_html=True)

    if len(df) > st.session_state["feed_limit"]:
        remaining = len(df) - st.session_state["feed_limit"]
        if st.button(f"Load more ({remaining} remaining)", width="stretch"):
            st.session_state["feed_limit"] += page_size
            st.rerun()
