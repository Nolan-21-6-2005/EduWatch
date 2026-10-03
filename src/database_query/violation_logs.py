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


def get_violation_report_kpis(
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:
    conditions = ["1 = 1"]
    params: list = []

    if start_date:
        conditions.append("date(v.thoi_gian) >= date(?)")
        params.append(start_date)

    if end_date:
        conditions.append("date(v.thoi_gian) <= date(?)")
        params.append(end_date)

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            COUNT(*) AS total_predictions,

            SUM(
                CASE
                    WHEN COALESCE(v.review_status, 'pending') = 'confirmed'
                    THEN 1
                    ELSE 0
                END
            ) AS confirmed_count,

            SUM(
                CASE
                    WHEN COALESCE(v.review_status, 'pending') = 'wrong'
                    THEN 1
                    ELSE 0
                END
            ) AS wrong_count,

            SUM(
                CASE
                    WHEN COALESCE(v.review_status, 'pending') = 'pending'
                    THEN 1
                    ELSE 0
                END
            ) AS pending_count

        FROM Violation_Logs v
        WHERE {where_clause}
    """

    with sqlite3.connect(getdatabase_path()) as conn:
        row = conn.execute(query, params).fetchone()

    return {
        "total_predictions": int(row[0] or 0),
        "confirmed": int(row[1] or 0),
        "wrong": int(row[2] or 0),
        "pending": int(row[3] or 0),
    }

def get_report_table(
    start_date: str | None = None,
    end_date: str | None = None,
):
    conditions = ["1 = 1"]
    params = []

    if start_date:
        conditions.append("date(v.thoi_gian) >= date(?)")
        params.append(start_date)

    if end_date:
        conditions.append("date(v.thoi_gian) <= date(?)")
        params.append(end_date)

    where_clause = " AND ".join(conditions)

    query = f"""
        SELECT
            date(v.thoi_gian) AS date,
            b.ten_toa AS building,
            r.ten_phong AS room,
            v.session AS session,

            COUNT(*) AS total_violations,

            SUM(
                CASE
                    WHEN COALESCE(v.review_status, 'pending') = 'confirmed'
                    THEN 1
                    ELSE 0
                END
            ) AS confirmed,

            SUM(
                CASE
                    WHEN COALESCE(v.review_status, 'pending') = 'wrong'
                    THEN 1
                    ELSE 0
                END
            ) AS wrong,

            SUM(
                CASE
                    WHEN COALESCE(v.review_status, 'pending') = 'pending'
                    THEN 1
                    ELSE 0
                END
            ) AS pending

        FROM Violation_Logs v

        LEFT JOIN Cameras c
            ON c.id = v.camera_id

        LEFT JOIN Rooms r
            ON r.id = c.room_id

        LEFT JOIN Buildings b
            ON b.id = r.building_id

        WHERE {where_clause}

        GROUP BY
            date(v.thoi_gian),
            b.ten_toa,
            r.ten_phong,
            v.session

        ORDER BY
            date(v.thoi_gian) DESC,
            b.ten_toa,
            r.ten_phong
    """

    with sqlite3.connect(getdatabase_path()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()

    return [dict(row) for row in rows]

def get_violation_type_distribution(
    start_date: str,
    end_date: str,
):
    with sqlite3.connect(getdatabase_path()) as conn:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                loai_vi_pham,
                COUNT(*) AS total
            FROM Violation_Logs
            WHERE DATE(thoi_gian)
                BETWEEN ? AND ?
            GROUP BY loai_vi_pham
            ORDER BY total DESC
            """,
            (start_date, end_date),
        )

        rows = cursor.fetchall()

        return [
            {
                "type": row[0],
                "total": row[1],
            }
            for row in rows
        ]

# =========================================================
# BIỂU ĐỒ ĐƯỜNG + LỊCH
# =========================================================

def get_violation_trend(
    start_date: str,
    end_date: str,
    granularity: str = "day",
) -> list[dict]:
    """
    Số vi phạm theo thời gian, đã điền 0 cho các mốc không có dữ liệu
    để đường biểu đồ liên tục.

    granularity:
        "day"   -> mỗi ngày trong [start_date, end_date]
        "month" -> mỗi tháng trong [start_date, end_date]
        "hour"  -> 24 giờ của start_date (dùng khi chọn 1 ngày trên lịch)

    Trả về: [{"label": "28/09", "total": 5}, ...] theo thứ tự thời gian.
    """
    import pandas as pd

    if granularity == "hour":
        sql_key = "strftime('%H', thoi_gian)"
        keys = [f"{h:02d}" for h in range(24)]
        labels = [f"{k}h" for k in keys]
    elif granularity == "month":
        sql_key = "strftime('%Y-%m', thoi_gian)"
        months = pd.period_range(start_date, end_date, freq="M")
        keys = [m.strftime("%Y-%m") for m in months]
        labels = [m.strftime("%m/%Y") for m in months]
    else:
        sql_key = "date(thoi_gian)"
        days = pd.date_range(start_date, end_date, freq="D")
        keys = [d.strftime("%Y-%m-%d") for d in days]
        labels = [d.strftime("%d/%m") for d in days]

    rows = _rows(
        f"""
        SELECT {sql_key} AS bucket, COUNT(*) AS total
        FROM Violation_Logs
        WHERE date(thoi_gian) BETWEEN date(?) AND date(?)
        GROUP BY bucket
        """,
        (start_date, end_date),
    )
    counts = {row["bucket"]: int(row["total"]) for row in rows}

    return [
        {"label": label, "total": counts.get(key, 0)}
        for key, label in zip(keys, labels)
    ]


def get_active_days(year: int, month: int) -> set[int]:
    """Các ngày (1..31) trong tháng có phát sinh log vi phạm - dùng để đánh dấu trên lịch."""
    rows = _rows(
        """
        SELECT DISTINCT CAST(strftime('%d', thoi_gian) AS INTEGER) AS day
        FROM Violation_Logs
        WHERE strftime('%Y-%m', thoi_gian) = ?
        """,
        (f"{year:04d}-{month:02d}",),
    )
    return {int(row["day"]) for row in rows}
