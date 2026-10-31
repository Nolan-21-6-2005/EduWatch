"""Shared HTML/CSS/data assembly for building-management panels."""

import json
from pathlib import Path

from fastapi.responses import HTMLResponse
from src.database_query.buildings_manager import get_locations

BASE_DIR = Path(__file__).resolve().parents[2]
ASSET_DIR = BASE_DIR / "view" / "asset"
STYLE_DIR = BASE_DIR / "view" / "style"


def render_locations_panel(*, viewer: bool = False) -> HTMLResponse:
    """Render either the editable admin panel or the read-only viewer panel."""
    template_name = "building_viewers.html" if viewer else "buildings.html"
    script_name = "building_viewers.js" if viewer else "buildings.js"
    css = (STYLE_DIR / "buildings.css").read_text(encoding="utf-8")

    template = (ASSET_DIR / template_name).read_text(encoding="utf-8")
    script = (ASSET_DIR / script_name).read_text(encoding="utf-8")
    data = json.dumps(get_locations(), ensure_ascii=False).replace("</", "<\\/")
    page = (
        template
        .replace("__BUILDINGS_CSS__", css)
        .replace("__BUILDINGS_DATA__", data)
        .replace("__API_BASE__", "")
        .replace("__BUILDINGS_JS__", script)
    )
    return HTMLResponse(page)
