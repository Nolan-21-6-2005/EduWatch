from utils.database_path import getdatabase_path
from pathlib import Path
import sqlite3

def get_buildings():
    conn = sqlite3.connect(getdatabase_path())
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ten_toa FROM Buildings
        WHERE is_deleted = ?
    """, (0, ))
    building = cursor.fetchall()
    print("Dữ liệu user lấy ra:", building) 
    
    conn.close()
    return building

def get_rooms(building_id: int):
    conn = sqlite3.connect(getdatabase_path())
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ten_phong FROM Rooms
        WHERE is_deleted = ? AND building_id = ?
    """, (0, building_id))
    
    room = cursor.fetchall()
    print("Dữ liệu user lấy ra:", room) 
    
    conn.close()
    return room

def get_cameras(room_id: int):
    conn = sqlite3.connect(getdatabase_path())
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, vi_tri_goc FROM Cameras
        WHERE status = ? AND room_id = ? 
    """, (1, room_id))
    
    camera = cursor.fetchall()
    print("Dữ liệu user lấy ra:", camera) 
    
    conn.close()
    return camera


def get_first_camera_id(building_name: str, room_name: str):
    """Lấy camera hoạt động đầu tiên của phòng được chọn, nếu tồn tại."""
    conn = sqlite3.connect(getdatabase_path())
    try:
        row = conn.execute(
            """
            SELECT c.id
            FROM Cameras c
            JOIN Rooms r ON r.id = c.room_id
            JOIN Buildings b ON b.id = r.building_id
            WHERE c.status = 1
              AND r.is_deleted = 0
              AND b.is_deleted = 0
              AND (b.ten_toa = ? OR b.ten_toa = ?)
              AND r.ten_phong = ?
            ORDER BY c.id
            LIMIT 1
            """,
            (building_name, building_name.replace("Giảng đường ", ""), room_name),
        ).fetchone()
        return row[0] if row else None
    finally:
        conn.close()
