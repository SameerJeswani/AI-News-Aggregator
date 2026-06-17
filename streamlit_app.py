"""
AI Signal Desk
Entry point for the Streamlit app. Wires together the sidebar filters
and the main dashboard, and injects the theme stylesheet.

Run with:  streamlit run streamlit_app.py
"""

from pathlib import Path

import streamlit as st

from app.ui.dashboard import render_dashboard
from app.ui.sidebar import render_sidebar
from app.ui.utils import generate_mock_articles

ROOT = Path(__file__).resolve().parent
CSS_PATH = ROOT / "assets" / "style.css"


def load_css(path: Path) -> None:
    if path.exists():
        st.markdown(f"<style>{path.read_text()}</style>", unsafe_allow_html=True)


def get_articles():
    """Cached mock dataset. Swap this for a real ingestion pipeline later —
    e.g. a function that pulls from your news API / scraper and returns the
    same dataframe shape (see generate_mock_articles in app/ui/utils.py)."""
    if "articles_df" not in st.session_state:
        st.session_state["articles_df"] = generate_mock_articles()
    return st.session_state["articles_df"]


def main() -> None:
    st.set_page_config(
        page_title="AI Signal Desk",
        page_icon=str(ROOT / "assets" / "logo.png"),
        layout="wide",
        initial_sidebar_state="expanded",
    )
    load_css(CSS_PATH)

    articles_df = get_articles()
    filters = render_sidebar()
    render_dashboard(articles_df, filters)


if __name__ == "__main__":
    main()
