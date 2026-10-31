import base64
from pathlib import Path
from src.database_query.violation_logs import get_violation_logs
BASE_DIR = Path(__file__).resolve().parents[2]

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


def payload(rows):
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