from src.utils.database_connection import connect_database, disconnect_database
import sqlite3
import hashlib
def get_user_by_email(email, password):
    conn = connect_database()
    cursor = conn.cursor()
    
    input_hash = hashlib.sha256(
        password.encode()
    ).hexdigest()   
    
    cursor.execute("""
        SELECT id, email, password, ho_ten, role 
        FROM Users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()
    disconnect_database(conn)
    if user is None:
        return {
            "success": False,
            "message": "User không tồn tại"
        }
    
    stored_hash = user[2]
    if input_hash == stored_hash:
        return {
            "success": True,
            "email": user[1],
            "fullname": user[3],
            "role": user[4]
        }
    else:
        return {
            "success": False,
            "message": "Wrong password"
        }    

