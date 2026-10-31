import base64
import html
import json
import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import src.services.violation_log_services as vls
from src.database_query.violation_logs import db_rows
from utils.helper import getdatabase_path
import utils.config as camera_state

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
ASSET_DIR = BASE_DIR / "view" / "asset"
STYLE_DIR = BASE_DIR / "view" / "style"

@router.get("/violations", response_model=list[dict])
def get_violations(limit: int = 100):
    """Trả nhật ký thật từ SQLite cho các client cần JSON."""
    limit = max(1, min(limit, 500))
    return vls.payload(db_rows(limit))


@router.get("/violations/panel", response_class=HTMLResponse)
def violation_panel():
    template = (ASSET_DIR / "violation_panel.html").read_text(encoding="utf-8")
    script = (ASSET_DIR / "violation_panel.js").read_text(encoding="utf-8")
    css = (STYLE_DIR / "violation.css").read_text(encoding="utf-8")
    data = json.dumps(vls.payload(db_rows(8)), ensure_ascii=False).replace("</", "<\\/")

    page = (
        template
        .replace("__VIOLATION_CSS__", css)
        .replace("__VIOLATION_DATA__", data)
        .replace("__API_BASE__", "http://localhost:8000")
        .replace("__VIOLATION_JS__", script)
    )
    return HTMLResponse(page)


@router.post("/violations/{violation_id}/review")
def review_violation(violation_id: int, payload: dict):
    status = vls.payload.get("status")
    if status not in {"confirmed", "wrong"}:
        raise HTTPException(status_code=400, detail="Trạng thái không hợp lệ")

    with sqlite3.connect(getdatabase_path()) as conn:
        cursor = conn.execute(
            """
            UPDATE Violation_Logs
            SET review_status = ?,
                is_confirmed = ?
            WHERE id = ?
            """,
            (status, 1 if status == "confirmed" else 0, violation_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy vi phạm")
        conn.commit()

    return {"status": status, "id": violation_id}
