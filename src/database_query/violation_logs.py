import sqlite3
from datetime import datetime
from pathlib import Path

from utils.database_path import getdatabase_path

BASE_DIR = Path(__file__).resolve().parents[2]


def _rows(query: str, params=()):
    with sqlite3.connect(getdatabase_path()) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(query, params).fetchall()


def get_violation_logs(
    *,
    limit: int | None = None,
    building_id: int | None = None,
    room_id: int | None = None,
    violation_type: str | None = None,
    review_status: str | None = None,
):
    query = """
        SELECT
            v.id,
            v.camera_id,
            v.loai_vi_pham,
            v.thoi_gian,
            v.image_path,
            v.confidence,
            v.is_confirmed,
            v.review_status,
            c.vi_tri_goc,
            c.status AS camera_status,
            r.id AS room_id,
            r.ten_phong,
            b.id AS building_id,
            b.ten_toa
        FROM Violation_Logs v
        LEFT JOIN Cameras c ON c.id = v.camera_id
        LEFT JOIN Rooms r ON r.id = c.room_id
        LEFT JOIN Buildings b ON b.id = r.building_id
        WHERE 1 = 1
    """
    params = []

    if building_id is not None:
        query += " AND b.id = ?"
        params.append(building_id)
    if room_id is not None:
        query += " AND r.id = ?"
        params.append(room_id)
    if violation_type:
        query += " AND v.loai_vi_pham = ?"
        params.append(violation_type)
    if review_status:
        query += " AND v.review_status = ?"
        params.append(review_status)

    query += " ORDER BY datetime(v.thoi_gian) DESC, v.id DESC"

    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    return _rows(query, params)


def get_latest_violations(limit=8):
    return get_violation_logs(limit=limit)


def _image_data_uri(image_path: str | None) -> str:
    if not image_path:
        return ""
    path = Path(image_path)
    if not path.is_absolute():
        path = BASE_DIR / path
    if not path.exists():
        return ""
    try:
        import base64
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


def violation_table_rows(limit: int | None = None):
    result = []
    for row in get_violation_logs(limit=limit):
        value = str(row["thoi_gian"] or "")
        try:
            dt = datetime.fromisoformat(value.replace("T", " "))
            display_time = dt.strftime("%d/%m/%Y %H:%M:%S")
        except ValueError:
            display_time = value

        result.append({
            "id": row["id"],
            "title": row["loai_vi_pham"] or "Vi phạm chưa xác định",
            "camera": row["vi_tri_goc"] or "Camera không xác định",
            "datetime_display": display_time,
            "thoi_gian": value,
            "building": row["ten_toa"] or "--",
            "room": row["ten_phong"] or "--",
            "building_id": row["building_id"],
            "room_id": row["room_id"],
            "confidence": float(row["confidence"] or 0),
            "review_status": row["review_status"] or "pending",
            "image": _image_data_uri(row["image_path"]),
        })
    return result
