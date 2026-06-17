"""Plotly charts for the Signal Desk, themed to match assets/style.css."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.ui.utils import CATEGORY_COLORS

FONT_BODY = "Inter, sans-serif"
FONT_MONO = "JetBrains Mono, monospace"
TEXT_SECONDARY = "#8B92A3"
TEXT_TERTIARY = "#5B6275"
BORDER = "#232838"
AMBER = "#FF8A3D"


def _base_layout(height: int) -> dict:
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family=FONT_BODY, color=TEXT_SECONDARY, size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        height=height,
        showlegend=False,
    )


def volume_over_time_chart(df: pd.DataFrame, days: int = 14) -> go.Figure:
    """Area chart of article count per day."""
    if df.empty:
        daily = pd.Series(dtype=int)
    else:
        daily = (
            df.assign(day=df["published_at"].dt.floor("D"))
            .groupby("day")
            .size()
            .sort_index()
        )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=daily.index,
            y=daily.values,
            mode="lines",
            line=dict(color=AMBER, width=2, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(255,138,61,0.12)",
            hovertemplate="%{x|%b %d}: %{y} articles<extra></extra>",
        )
    )
    fig.update_layout(**_base_layout(240))
    fig.update_xaxes(
        showgrid=False, color=TEXT_TERTIARY, tickfont=dict(family=FONT_MONO, size=10)
    )
    fig.update_yaxes(
        showgrid=True, gridcolor=BORDER, zeroline=False,
        color=TEXT_TERTIARY, tickfont=dict(family=FONT_MONO, size=10),
    )
    return fig


def category_breakdown_chart(df: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart of article counts per category."""
    if df.empty:
        counts = pd.Series(dtype=int)
    else:
        counts = df["category"].value_counts().sort_values()

    colors = [CATEGORY_COLORS.get(c, AMBER) for c in counts.index]

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=counts.values,
            y=counts.index,
            orientation="h",
            marker=dict(color=colors),
            hovertemplate="%{y}: %{x} articles<extra></extra>",
        )
    )
    fig.update_layout(**_base_layout(240))
    fig.update_xaxes(
        showgrid=True, gridcolor=BORDER, zeroline=False,
        color=TEXT_TERTIARY, tickfont=dict(family=FONT_MONO, size=10),
    )
    fig.update_yaxes(
        showgrid=False, color=TEXT_SECONDARY, tickfont=dict(family=FONT_BODY, size=11),
    )
    return fig


def render_charts(df: pd.DataFrame) -> None:
    """Render the two-panel chart row."""
    col_a, col_b = st.columns([2, 1])

    with col_a:
        with st.container(border=True):
            st.markdown(
                '<div class="chart-panel__title">Signal volume over time</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(
                volume_over_time_chart(df),
                width="stretch",
                config={"displayModeBar": False},
            )

    with col_b:
        with st.container(border=True):
            st.markdown(
                '<div class="chart-panel__title">By category</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(
                category_breakdown_chart(df),
                width="stretch",
                config={"displayModeBar": False},
            )
