from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_PATH = BASE_DIR / "data_model" / "eduwatch.db"

def connect_database():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def disconnect_database(conn):
    if conn:
        try:
            conn.commit()
        except sqlite3.ProgrammingError:
            # Phòng trường hợp câu lệnh SELECT không cần commit hoặc kết nối đã đóng trước đó
            pass
        conn.close()
