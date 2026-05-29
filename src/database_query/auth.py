from pathlib import Path
import sqlite3
from utils.database_path import getdatabase_path

def signin(email: str):
    conn = sqlite3.connect(getdatabase_path())
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, email, password, role FROM Users
        WHERE email = ?
    """, (email,))
    user = cursor.fetchone()
    
    print("Dữ liệu user lấy ra:", user) 
    
    conn.close()
    return user
    
#Kiểm tra độ mạnh của mật khẩu
def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and      # chữ hoa
        re.search(r"[a-z]", password) and      # chữ thường
        re.search(r"[0-9]", password) and      # số
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)  # ký tự đặc biệt
    )
def getUsername():
    return (
    
    )
#Chuc nang dang ky
def signup(username, password, check_password):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if is_strong_password(password) and password == check_password:
            cursor.execute("""
            INSERT INTO users (username, password, email, gender, phone, date, role)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (username, password, email, gender, phone, date, role))
            return True
        else: return False


