import json
import urllib.parse
from pathlib import Path
import streamlit as st

_COMPONENT_DIR = Path(__file__).resolve().parent
_ASSET_DIR = _COMPONENT_DIR.parent / "asset"
_STYLE_DIR = _COMPONENT_DIR.parent / "style"

_TABLE_HTML = (_ASSET_DIR / "admin_table.html").read_text(encoding="utf-8")
_TABLE_JS = (_ASSET_DIR / "admin_table.js").read_text(encoding="utf-8")
_TABLE_CSS = (_STYLE_DIR / "table.css").read_text(encoding="utf-8")


def _component_html(
    table_type: str,
    data: list[dict],
    *,
    api_base: str = "http://127.0.0.1:8000",
) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    return (
        _TABLE_HTML
        .replace("__TABLE_CSS__", _TABLE_CSS)
        .replace("__TABLE_DATA__", payload)
        .replace("__TABLE_TYPE__", table_type)
        .replace("__API_BASE__", api_base.rstrip("/"))
        .replace("__TABLE_JS__", _TABLE_JS)
    )


def render_admin_table(
    table_type: str,
    data: list[dict],
    *,
    api_base: str = "http://127.0.0.1:8000",
    height: int = 720,
):
    # Tạo nội dung HTML hoàn chỉnh
    html_content = _component_html(table_type, data, api_base=api_base)
    
    # Mã hóa chuỗi HTML thành Data URI để truyền vào st.iframe()
    encoded_html = urllib.parse.quote(html_content)
    data_url = f"data:text/html;charset=utf-8,{encoded_html}"
    
    # Sử dụng st.iframe() thay cho streamlit.components.v1
    st.iframe(data_url, height=height)
