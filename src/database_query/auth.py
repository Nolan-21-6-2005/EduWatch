from pathlib import Path
import sqlite3
from utils.database_path import getdatabase_path

def login(professor_id: str):
    conn = sqlite3.connect(getdatabase_path())
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, ma_giang_vien, password, role FROM Users
        WHERE ma_giang_vien = ?
    """, (professor_id,))
    user = cursor.fetchone()
    
    print("Dữ liệu user lấy ra:", user) 
    
    conn.close()
    return user
    
#Chuc nang dang ky
def signup(professor_id, password, role, 
           ho_ten, ngay_sinh, gioi_tinh, 
           email, so_dien_thoai, anh_dai_dien, 
           created_at, status):
           
    conn = sqlite3.connect(getdatabase_path())
    cursor = conn.cursor()

    user = cursor.execute("""
    INSERT INTO Users (ma_giang_vien, password, role, ho_ten, ngay_sinh, gioi_tinh, email, so_dien_thoai, anh_dai_dien, created_at, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (professor_id, password, role, ho_ten, ngay_sinh, gioi_tinh, email, so_dien_thoai, anh_dai_dien, created_at, status))
    conn.commit()
    conn.close()
    return True


