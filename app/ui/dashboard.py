"""Main dashboard layout: ticker, header, metrics, charts, and the news feed."""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from app.ui.cards import render_metric_cards, render_news_feed
from app.ui.charts import render_charts
from app.ui.utils import compute_stats, filter_articles


def render_ticker(df: pd.DataFrame, n: int = 8) -> None:
    """Scrolling marquee of the most recent headlines (signature element)."""
    headlines = df.sort_values("published_at", ascending=False)["title"].head(n).tolist()
    if not headlines:
        return
    # Duplicate the list so the CSS marquee (translateX -50%) loops seamlessly.
    items = "".join(f"<span><b>{h}</b></span>" for h in headlines * 2)
    st.markdown(
        f"""
        <div class="signal-ticker">
            <div class="signal-ticker__badge">
                <span class="signal-ticker__dot"></span>LIVE
            </div>
            <div class="signal-ticker__track">{items}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    now = datetime.now().strftime("%b %d, %Y · %H:%M")
    st.markdown(
        f"""
        <div class="desk-header">
            <div>
                <h1>AI Signal Desk</h1>
                <p>Tracking research, funding, and policy signals across the AI industry.</p>
            </div>
            <div class="desk-header__meta">LAST SYNCED<br>{now}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(full_df: pd.DataFrame, filters: dict) -> None:
    render_ticker(full_df)
    render_header()

    filtered = filter_articles(
        full_df,
        categories=filters["categories"],
        sentiments=filters["sentiments"],
        sources=filters["sources"],
        days=filters["days"],
        query=filters["query"],
    )

    if filters["sort_by"] == "Highest impact":
        filtered = filtered.sort_values("impact_score", ascending=False).reset_index(drop=True)

    # Reset feed pagination whenever the active filter set changes.
    filter_signature = str(filters)
    if st.session_state.get("_filter_signature") != filter_signature:
        st.session_state["_filter_signature"] = filter_signature
        st.session_state["feed_limit"] = 12

    stats = compute_stats(filtered, full_df)
    render_metric_cards(stats)

    st.markdown(
        '<div class="section-label">Trends</div>',
        unsafe_allow_html=True,
    )
    render_charts(filtered)

    st.markdown(
        f'<div class="section-label"><span>Latest Signals</span>'
        f'<span>{stats["total_filtered"]} matching</span></div>',
        unsafe_allow_html=True,
    )
    render_news_feed(filtered)
