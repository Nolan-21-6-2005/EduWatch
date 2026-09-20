import base64
import html
import sqlite3
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from utils.database_path import getdatabase_path

router = APIRouter()
BASE_DIR = Path(__file__).resolve().parents[2]


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
        suffix = path.suffix.lower()
        mime = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
        }.get(suffix, "image/jpeg")
        return f"data:{mime};base64,{encoded}"
    except OSError:
        return ""


def _format_time(value: str | None) -> str:
    if not value:
        return "--:--:--"
    value = str(value).replace("T", " ")
    return value[-8:] if len(value) >= 8 else value


def _status(status: str | None):
    if status == "confirmed":
        return "ĐÃ XÁC NHẬN", "confirmed"
    if status == "wrong":
        return "ĐÃ BÁO SAI", "wrong"
    return "CHỜ XÁC NHẬN", "pending"


def _card(row):
    title = html.escape(row["loai_vi_pham"] or "Vi phạm chưa xác định")
    camera = html.escape(row["vi_tri_goc"] or "Camera không xác định")
    room = html.escape(row["ten_phong"] or "--")
    building = html.escape(row["ten_toa"] or "--")
    time = html.escape(_format_time(row["thoi_gian"]))
    confidence = float(row["confidence"] or 0) * 100
    status_text, status_class = _status(row["review_status"])
    image = _image_data_uri(row["image_path"])
    image_html = (
        f'<img src="{image}" alt="Ảnh bằng chứng" />'
        if image
        else '<div class="evidence-empty">Không có ảnh bằng chứng</div>'
    )

    return f"""
    <article class="violation-card" data-id="{row['id']}">
      <div class="card-topline">
        <div>
          <div class="camera-name">Cam: {camera}</div>
          <div class="violation-time">{time}</div>
        </div>
        <span class="status {status_class}">{status_text}</span>
      </div>

      <div class="violation-title">{title}</div>
      <div class="location">{building} · {room}</div>

      <div class="evidence-wrap">
        {image_html}
        <span class="confidence">Độ tin cậy: {confidence:.1f}%</span>
      </div>

      <div class="actions">
        <button class="confirm" onclick="reviewViolation({row['id']}, 'confirmed', this)">
          ✓&nbsp; Xác nhận
        </button>
        <button class="wrong" onclick="reviewViolation({row['id']}, 'wrong', this)">
          ×&nbsp; Báo sai AI
        </button>
      </div>
    </article>
    """


@router.get("/violations/panel", response_class=HTMLResponse)
def violation_panel():
    rows = _db_rows()
    cards = "".join(_card(row) for row in rows)

    if not cards:
        cards = '<div class="empty">Chưa có vi phạm mới.</div>'

    page = f"""
<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Nhật ký vi phạm</title>
<style>
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; background: transparent; font-family: Inter, Arial, sans-serif; color: #18212f; }}
body {{ padding: 16px 14px 18px; }}
.panel {{ min-height: 100vh; }}
.panel-header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }}
.panel-title {{ font-size:14px; font-weight:800; letter-spacing:.08em; }}
.dot {{ width:8px; height:8px; border-radius:50%; background:#e25563; }}
.feed {{ display:flex; flex-direction:column; gap:16px; }}
.violation-card {{ background:#f7f9fa; border:1px solid #e2e8ec; border-radius:18px; padding:16px; box-shadow:0 3px 14px rgba(24,33,47,.05); }}
.card-topline {{ display:flex; justify-content:space-between; gap:10px; align-items:flex-start; }}
.camera-name {{ font-size:12px; color:#4d5966; }}
.violation-time {{ margin-top:5px; font-size:12px; color:#18212f; font-weight:600; }}
.status {{ flex:none; padding:5px 9px; border-radius:999px; font-size:9px; font-weight:800; white-space:nowrap; }}
.status.pending {{ background:#fff1c9; color:#a66a00; }}
.status.confirmed {{ background:#dff7e9; color:#14844c; }}
.status.wrong {{ background:#fde4e6; color:#c53d4a; }}
.violation-title {{ margin:14px 0 10px; font-size:16px; line-height:1.3; font-weight:700; color:#d13e4c; }}
.location {{ margin-bottom:10px; font-size:11px; color:#7b8793; }}
.evidence-wrap {{ position:relative; overflow:hidden; border-radius:14px; background:#dfe5e9; aspect-ratio: 16 / 8.5; }}
.evidence-wrap img {{ width:100%; height:100%; object-fit:cover; display:block; }}
.evidence-empty {{ width:100%; height:100%; display:grid; place-items:center; color:#7c8792; font-size:11px; }}
.confidence {{ position:absolute; left:9px; bottom:8px; background:#d43e4c; color:#fff; padding:5px 8px; border-radius:7px; font-size:10px; font-weight:800; }}
.actions {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-top:12px; }}
.actions button {{ border:0; border-radius:999px; min-height:40px; font-size:12px; font-weight:750; cursor:pointer; }}
.actions .confirm {{ background:#2dbb6d; color:#fff; }}
.actions .wrong {{ background:#e5e8ea; color:#18212f; }}
.actions button:disabled {{ opacity:.55; cursor:default; }}
.empty {{ padding:40px 15px; text-align:center; color:#87929e; background:#f7f9fa; border:1px dashed #dce3e8; border-radius:16px; }}
.footer-link {{ margin-top:16px; display:flex; align-items:center; justify-content:center; min-height:44px; border:1px solid #2dbb6d; border-radius:999px; color:#13804a; font-size:11px; font-weight:800; letter-spacing:.08em; }}
@media (max-width: 850px) {{ body {{ padding:12px 8px; }} .violation-card {{ padding:12px; }} }}
</style>
</head>
<body>
<div class="panel">
  <div class="panel-header">
    <div class="panel-title">NHẬT KÝ VI PHẠM MỚI NHẤT</div>
    <span class="dot"></span>
  </div>
  <div class="feed">{cards}</div>
  <div class="footer-link">XEM TẤT CẢ LỊCH SỬ</div>
</div>
<script>
async function reviewViolation(id, status, button) {{
  button.disabled = true;
  try {{
    const response = await fetch(`/violations/${id}/review`, {{
      method: 'POST',
      headers: {{ 'Content-Type': 'application/json' }},
      body: JSON.stringify({{ status }})
    }});
    if (!response.ok) throw new Error('Không thể cập nhật');
    window.location.reload();
  }} catch (error) {{
    console.error(error);
    button.disabled = false;
    alert('Không thể cập nhật trạng thái vi phạm.');
  }}
}}
</script>
</body>
</html>
"""
    return HTMLResponse(page)


@router.post("/violations/{violation_id}/review")
def review_violation(violation_id: int, payload: dict):
    status = payload.get("status")
    if status not in {"confirmed", "wrong"}:
        raise HTTPException(status_code=400, detail="Trạng thái không hợp lệ")

    with sqlite3.connect(getdatabase_path()) as conn:
        cursor = conn.execute(
            "UPDATE Violation_Logs SET review_status = ? WHERE id = ?",
            (status, violation_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy vi phạm")
        conn.commit()

    return {"status": status, "id": violation_id}
