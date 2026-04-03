import streamlit as st
import sqlite3
import sys

sys.path.append('/var/home/namson/Webdevelopment/model')
st.title("Đăng nhập tài khoản")
username = st.text_input("Email hoac Username:")
password = st.text_input("Password:", type = "password")
role = st.selectbox(
    "Vai trò:",
    ("Professor", "Supervisory", "Admin"),
)
sign_in = st.button("Đăng nhập")

def signin(username, password):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username = ? AND password = ?
    """, (username, password))

    user = cursor.fetchone()
    conn.close()

    return user is not None

if sign_in:
    if signin(username, password):
        if role == "Professor": 
            st.switch_page("pages/professor.py")
        elif role == "Supervisory":
            st.switch_page("pages/camera.py")
        else:
            st.switch_page("pages/admin.py")
        st.success("Đăng nhập thành công")
    else:
        st.error("Sai thông tin")

if st.button("Đăng ký"):
    st.switch_page("pages/sign_up.py")
