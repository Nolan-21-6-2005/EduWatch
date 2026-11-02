from view.component.report_list import render_request_list
from src.database_query import notifications as db
import pandas as pd
import streamlit as st

def _load_records(kind: str) -> pd.DataFrame:
    user_code = st.session_state.get("professor_id")

    if not user_code:
        return pd.DataFrame()

    if kind == "issue":
        records = db.get_incident_requests(user_code)
    elif kind == "field":
        records = db.get_field_report_requests(user_code)
    else:
        return pd.DataFrame()

    return pd.DataFrame(records)
