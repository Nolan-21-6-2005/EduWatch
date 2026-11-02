import streamlit as st
from html import escape
from src.database_query.profile import get_user_by_code, get_user_by_id

def _get_logged_in_user() -> dict | None:
    user_id = st.session_state.get("user_id")
    if user_id:
        user = get_user_by_id(int(user_id))
        if user:
            return user

    professor_id = str(st.session_state.get("professor_id", "")).strip()
    if professor_id:
        return get_user_by_code(professor_id)

    return None


def _profile_field(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="ew-profile-field">
            <div class="ew-profile-field-label">{escape(label)}</div>
            <div class="ew-profile-field-value">{escape(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )