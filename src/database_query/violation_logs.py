import sqlite3
from utils.database_path import getdatabase_path


def get_latest_violations(limit=8):
    query = """
        SELECT v.id, v.camera_id, v.loai_vi_pham, v.thoi_gian,
               v.image_path, v.confidence, v.is_confirmed,
               v.review_status, c.vi_tri_goc, r.ten_phong, b.ten_toa
        FROM Violation_Logs v
        LEFT JOIN Cameras c ON c.id = v.camera_id
        LEFT JOIN Rooms r ON r.id = c.room_id
        LEFT JOIN Buildings b ON b.id = r.building_id
        ORDER BY datetime(v.thoi_gian) DESC, v.id DESC
        LIMIT ?
    """
    with sqlite3.connect(getdatabase_path()) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(query, (limit,)).fetchall()
