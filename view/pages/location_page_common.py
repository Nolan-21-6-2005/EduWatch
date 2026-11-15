"""Shared Streamlit wrapper for building-related pages."""

import streamlit as st


def render_location_page(*, title: str, page_title: str, panel_url: str) -> None:
    st.set_page_config(layout="wide", page_title=page_title)
    st.markdown(
        f"""
        <div class=\"page-header\">
            <div>
                <h1 class=\"page-header-title\">{title}</h1>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.iframe(panel_url, height=760)
