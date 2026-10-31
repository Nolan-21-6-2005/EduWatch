import sqlite3
from pathlib import Path

from utils.helper import getdatabase_path

BASE_DIR = Path(__file__).resolve().parents[2]


def _rows(query: str, params=()):
    with sqlite3.connect(getdatabase_path()) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(query, params).fetchall()


def db_rows(limit: int = 8):
    query = """
        SELECT v.id, v.loai_vi_pham, v.thoi_gian, v.image_path,
               v.confidence, v.review_status, c.vi_tri_goc,
               r.ten_phong, b.ten_toa
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


def get_violation_logs(
    *,
    limit: int | None = None,
    building_id: int | None = None,
    room_id: int | None = None,
    violation_type: str | None = None,
    review_status: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    query = """
        SELECT
            v.id, v.camera_id, v.loai_vi_pham, v.thoi_gian,
            v.image_path, v.confidence, v.is_confirmed,
            v.review_status, v.session AS session,
            c.vi_tri_goc, c.status AS camera_status,
            r.id AS room_id, r.ten_phong,
            b.id AS building_id, b.ten_toa
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
    if violation_type is not None:
        query += " AND v.loai_vi_pham = ?"
        params.append(violation_type)
    if review_status is not None:
        query += " AND COALESCE(v.review_status, 'pending') = ?"
        params.append(review_status)
    if start_date is not None:
        query += " AND date(v.thoi_gian) >= date(?)"
        params.append(start_date)
    if end_date is not None:
        query += " AND date(v.thoi_gian) <= date(?)"
        params.append(end_date)

    query += " ORDER BY datetime(v.thoi_gian) DESC, v.id DESC"

    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    return _rows(query, params)


def get_violation_report_kpis(
    session: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> dict:

    conditions = ["v.review_status = 'confirmed'"]
    params = []

    if start_date:
        conditions.append("date(v.thoi_gian) >= date(?)")
        params.append(start_date)

    if end_date:
        conditions.append("date(v.thoi_gian) <= date(?)")
        params.append(end_date)

    if session:
        conditions.append("v.session = ?")
        params.append(session)

    query = f"""
        WITH filtered_logs AS (
            SELECT v.loai_vi_pham
            FROM Violation_Logs v
            WHERE {" AND ".join(conditions)}
        ),
        total AS (
            SELECT COUNT(*) AS total_violations
            FROM filtered_logs
        ),
        most_common AS (
            SELECT
                loai_vi_pham
            FROM filtered_logs
            GROUP BY loai_vi_pham
            ORDER BY COUNT(*) DESC
            LIMIT 1
        )
        SELECT
            total.total_violations,
            most_common.loai_vi_pham
        FROM total
        LEFT JOIN most_common ON 1 = 1
    """

    with sqlite3.connect(getdatabase_path()) as conn:
        row = conn.execute(query, params).fetchone()

    return {
        "confirmed": int(row[0] or 0),
        "violation_type": str(row[1] or "")
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

    query = f"""
        SELECT
            date(v.thoi_gian) AS date,
            b.ten_toa AS building,
            r.ten_phong AS room,
            v.session AS session,
            COUNT(*) AS total_violations,
            SUM(CASE WHEN COALESCE(v.review_status, 'pending') = 'confirmed'
                     THEN 1 ELSE 0 END) AS confirmed,
            SUM(CASE WHEN COALESCE(v.review_status, 'pending') = 'wrong'
                     THEN 1 ELSE 0 END) AS wrong,
            SUM(CASE WHEN COALESCE(v.review_status, 'pending') = 'pending'
                     THEN 1 ELSE 0 END) AS pending
        FROM Violation_Logs v
        LEFT JOIN Cameras c ON c.id = v.camera_id
        LEFT JOIN Rooms r ON r.id = c.room_id
        LEFT JOIN Buildings b ON b.id = r.building_id
        WHERE {" AND ".join(conditions)}
        GROUP BY date(v.thoi_gian), b.ten_toa, r.ten_phong, v.session
        ORDER BY date(v.thoi_gian) DESC, b.ten_toa, r.ten_phong
    """

    with sqlite3.connect(getdatabase_path()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()

    return [dict(row) for row in rows]


def get_violation_type_distribution(
    start_date: str,
    end_date: str,
    *,
    session: str | None = None,
):
    conditions = ["DATE(thoi_gian) BETWEEN ? AND ?"]
    params = [start_date, end_date]

    if session is not None:
        if session not in {"exam", "study"}:
            raise ValueError("session phải là 'exam', 'study' hoặc None")
        conditions.append("session = ?")
        params.append(session)

    query = f"""
        SELECT loai_vi_pham, COUNT(*) AS total
        FROM Violation_Logs
        WHERE {" AND ".join(conditions)}
        GROUP BY loai_vi_pham
        ORDER BY total DESC, loai_vi_pham
    """

    with sqlite3.connect(getdatabase_path()) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()

    return [{"type": row[0], "total": row[1]} for row in rows]


def get_violation_trend(
    start_date: str,
    end_date: str,
    *,
    group_by: str = "day",
) -> list[dict]:
    """Lấy tổng số log vi phạm theo ngày hoặc theo tháng trong khoảng đã chọn."""
    if group_by == "month":
        date_expression = "strftime('%Y-%m', v.thoi_gian)"
    else:
        date_expression = "date(v.thoi_gian)"

    query = f"""
        SELECT {date_expression} AS period, COUNT(*) AS total
        FROM Violation_Logs v
        WHERE date(v.thoi_gian) >= date(?)
          AND date(v.thoi_gian) <= date(?)
        GROUP BY period
        ORDER BY period
    """

    with sqlite3.connect(getdatabase_path()) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, (start_date, end_date)).fetchall()

    return [
        {"period": row["period"], "total": int(row["total"] or 0)}
        for row in rows
    ]
