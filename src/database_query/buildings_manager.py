from utils.database_path import getdatabase_path
from pathlib import Path
import sqlite3

def get_buildings(building_id):
    conn = sqlite3.connect(getdatabase_path())
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id ten_toa FROM Buildings
        WHERE is_deleted = ? AND id = ?
    """, (0, building_id))
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
        WHERE is_deleted = ? AND 
    """, (0, building_id))
    
    camera = cursor.fetchall()
    print("Dữ liệu user lấy ra:", camera) 
    
    conn.close()
    return camera