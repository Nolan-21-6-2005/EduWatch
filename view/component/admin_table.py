import json
from pathlib import Path
import streamlit.components.v1 as components


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
    components.html(
        _component_html(table_type, data, api_base=api_base),
        height=height,
        scrolling=False,
    )
