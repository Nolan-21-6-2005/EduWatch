import base64
import html
import json
import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from utils.database_path import getdatabase_path

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]
ASSET_DIR = BASE_DIR / "view" / "asset"
STYLE_DIR = BASE_DIR / "view" / "style"


def _db_rows(limit: int = 8):
    query = """
        SELECT
            v.id,
            v.loai_vi_pham,
            v.thoi_gian,
            v.image_path,
            v.confidence,
            v.review_status,
            c.vi_tri_goc,
            r.ten_phong,
            b.ten_toa
        FROM Violation_Logs AS v
        LEFT JOIN Cameras AS c ON c.id = v.camera_id
        LEFT JOIN Rooms AS r ON r.id = c.room_id
        LEFT JOIN Buildings AS b ON b.id = r.building_id
        ORDER BY datetime(v.thoi_gian) DESC, v.id DESC
        LIMIT ?
    """
    with sqlite3.connect(getdatabase_path()) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(query, (limit,)).fetchall()


def _image_data_uri(image_path: str | None) -> str:
    if not image_path:
        return ""
    path = Path(image_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    if not path.exists():
        return ""
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        mime = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }.get(path.suffix.lower(), "image/jpeg")
        return f"data:{mime};base64,{encoded}"
    except OSError:
        return ""


def _format_time(value: str | None) -> str:
    if not value:
        return "--"
    return str(value).replace("T", " ")


def _payload(rows):
    return [
        {
            "id": row["id"],
            "title": row["loai_vi_pham"] or "Vi phạm chưa xác định",
            "camera": row["vi_tri_goc"] or "Camera không xác định",
            "datetime_display": _format_time(row["thoi_gian"]),
            "building": row["ten_toa"] or "--",
            "room": row["ten_phong"] or "--",
            "confidence": float(row["confidence"] or 0),
            "review_status": row["review_status"] or "pending",
            "image": _image_data_uri(row["image_path"]),
        }
        for row in rows
    ]


@router.get("/violations", response_model=list[dict])
def get_violations(limit: int = 100):
    """Trả nhật ký thật từ SQLite cho các client cần JSON."""
    limit = max(1, min(limit, 500))
    return _payload(_db_rows(limit))


@router.get("/violations/panel", response_class=HTMLResponse)
def violation_panel():
    template = (ASSET_DIR / "violation_panel.html").read_text(encoding="utf-8")
    script = (ASSET_DIR / "violation_panel.js").read_text(encoding="utf-8")
    css = (STYLE_DIR / "violation.css").read_text(encoding="utf-8")
    data = json.dumps(_payload(_db_rows(8)), ensure_ascii=False).replace("</", "<\\/")

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
    status = payload.get("status")
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
