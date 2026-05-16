import sqlite3
from src.utils.database_connection import connect_database disconnect_database

def insert_log(violation_type, confidence, evidence_path):
    """Hàm này sẽ được gọi bên phía AI Service khi phát hiện vi phạm"""
    conn = connect_database()
    cursor = conn.cursor()
    current_time = datetime.now().strftime("%H:%M:%S")
    cursor.execute('''
        INSERT INTO violation_logs (time, type, confidence, status, evidence_path)
        VALUES (?, ?, ?, ?, ?)
    ''', (current_time, violation_type, f"{int(confidence * 100)}%", "⏳ Chờ duyệt", evidence_path))
    conn.commit()
    conn.close()

def get_all_logs():
    """Lấy toàn bộ danh sách log để hiển thị lên bảng NiceGUI"""
    conn = sqlite3.connect(DB_PATH)
    # Cấu hình này giúp trả về dữ liệu dạng Dictionary (khớp với AG Grid) thay vì dạng Tuple
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM violation_logs ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def update_log_status(log_id, new_status):
    """Cập nhật trạng thái duyệt lỗi khi Giám thị bấm nút"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('UPDATE violation_logs SET status = ? WHERE id = ?', (new_status, log_id))
    conn.commit()
    conn.close()
