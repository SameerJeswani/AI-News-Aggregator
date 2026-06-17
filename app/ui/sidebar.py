"""Sidebar: brand mark + filter controls for the Signal Desk."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

from app.ui.utils import CATEGORIES, SENTIMENTS, SOURCES

LOGO_PATH = Path(__file__).resolve().parent.parent.parent / "assets" / "logo.png"


def _logo_b64() -> str:
    if LOGO_PATH.exists():
        return base64.b64encode(LOGO_PATH.read_bytes()).decode()
    return ""


def render_sidebar() -> dict:
    """Render sidebar controls and return the selected filter values."""
    with st.sidebar:
        logo_b64 = _logo_b64()
        logo_tag = f'<img src="data:image/png;base64,{logo_b64}" />' if logo_b64 else ""
        st.markdown(
            f"""
            <div class="sidebar-brand">
                {logo_tag}
                <div>
                    <div class="sidebar-brand__name">AI Signal Desk</div>
                    <div class="sidebar-brand__tag">FRONTIER NEWS, FILTERED</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        query = st.text_input(
            "Search",
            placeholder="Search headlines, companies...",
            label_visibility="collapsed",
            key="flt_query",
        )

        st.markdown('<div class="sidebar-filter-label">Timeframe</div>', unsafe_allow_html=True)
        timeframe = st.radio(
            "Timeframe",
            options=["Today", "3 days", "7 days", "14 days", "All"],
            index=3,
            label_visibility="collapsed",
            key="flt_timeframe",
        )
        days_map = {"Today": 1, "3 days": 3, "7 days": 7, "14 days": 14, "All": None}

        st.markdown('<div class="sidebar-filter-label">Category</div>', unsafe_allow_html=True)
        categories = st.multiselect(
            "Category",
            options=CATEGORIES,
            default=[],
            label_visibility="collapsed",
            placeholder="All categories",
            key="flt_categories",
        )

        st.markdown('<div class="sidebar-filter-label">Sentiment</div>', unsafe_allow_html=True)
        sentiments = st.multiselect(
            "Sentiment",
            options=SENTIMENTS,
            default=[],
            label_visibility="collapsed",
            placeholder="All sentiment",
            key="flt_sentiments",
        )

        st.markdown('<div class="sidebar-filter-label">Sources</div>', unsafe_allow_html=True)
        sources = st.multiselect(
            "Sources",
            options=SOURCES,
            default=[],
            label_visibility="collapsed",
            placeholder="All sources",
            key="flt_sources",
        )

        st.markdown('<div class="sidebar-filter-label">Sort by</div>', unsafe_allow_html=True)
        sort_by = st.selectbox(
            "Sort by",
            options=["Most recent", "Highest impact"],
            label_visibility="collapsed",
            key="flt_sort_by",
        )

        st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

        if st.button("Reset filters", width="stretch"):
            for k in (
                "flt_query", "flt_timeframe", "flt_categories",
                "flt_sentiments", "flt_sources", "flt_sort_by",
            ):
                st.session_state.pop(k, None)
            st.rerun()

    return {
        "query": query,
        "days": days_map[timeframe],
        "categories": categories,
        "sentiments": sentiments,
        "sources": sources,
        "sort_by": sort_by,
    }
