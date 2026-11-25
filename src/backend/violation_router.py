import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
import src.services.violation_log_services as vls
from src.database_query.violation_logs import count_pending_violations, db_rows
from src.services import live_events
from utils.config import SESSION_LABELS
from utils.db import connect as db_connect

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
ASSET_DIR = BASE_DIR / "view" / "asset"
STYLE_DIR = BASE_DIR / "view" / "style"

@router.get("/violations", response_model=list[dict])
def get_violations(limit: int = 100, session: str | None = None):
    """Trả nhật ký thật từ SQLite cho các client cần JSON (lọc theo exam/study nếu có)."""
    limit = max(1, min(limit, 500))
    return vls.payload(db_rows(limit, SESSION_LABELS.get(session)))


@router.get("/violations/live")
def violations_live(session: str | None = None, since: int | None = None, limit: int = 8):
    """Dữ liệu cho panel thời gian thực.

    Nếu ``since`` bằng phiên bản hiện tại thì chưa có gì mới: trả ngay, không truy vấn DB.
    Đọc phiên bản TRƯỚC khi truy vấn để không bỏ lỡ log được ghi giữa hai bước.
    """
    current = live_events.version()
    if since is not None and since == current:
        return {"changed": False, "version": current}
    labels = SESSION_LABELS.get(session)
    limit = max(1, min(limit, 50))
    return {
        "changed": True,
        "version": current,
        "pending": count_pending_violations(labels),
        "rows": vls.payload(db_rows(limit, labels), inline_images=False),
    }


@router.get("/violations/panel", response_class=HTMLResponse)
def violation_panel(session: str | None = None):
    """session=exam: tất cả vi phạm phòng thi; session=study: vi phạm phòng thường + dùng chung."""
    labels = SESSION_LABELS.get(session)
    template = (ASSET_DIR / "violation_panel.html").read_text(encoding="utf-8")
    script = (ASSET_DIR / "violation_panel.js").read_text(encoding="utf-8")
    css = (STYLE_DIR / "violation.css").read_text(encoding="utf-8")
    data = json.dumps(vls.payload(db_rows(8, labels), inline_images=False), ensure_ascii=False).replace("</", "<\\/")

    page = (
        template
        .replace("__VIOLATION_CSS__", css)
        .replace("__VIOLATION_DATA__", data)
        .replace("__PENDING_COUNT__", str(count_pending_violations(labels)))
        .replace("__API_BASE__", "")  # cùng origin với trang: dùng đường dẫn tương đối
        .replace("__SESSION__", session if session in SESSION_LABELS else "")
        .replace("__VERSION__", str(live_events.version()))
        .replace("__VIOLATION_JS__", script)
    )
    return HTMLResponse(page)


@router.post("/violations/{violation_id}/review")
def review_violation(violation_id: int, payload: dict):
    status = payload.get("status")
    if status not in {"confirmed", "wrong", "pending"}:
        raise HTTPException(status_code=400, detail="Trạng thái không hợp lệ")

    with db_connect() as conn:
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

    live_events.notify()  # mọi panel đang mở cập nhật trạng thái ngay
    return {"status": status, "id": violation_id}
