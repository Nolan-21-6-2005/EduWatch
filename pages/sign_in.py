import streamlit as st
import sqlite3
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "model" / "database.db"
col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("EduWatch VNUA")
    st.markdown("""
    <header>
        <h2>Kiến tạo tương lai <br> số hóa giáo dục</h2>
    </header>
    <body>
        <p>Hệ thống giám sát và quản lý đào tạo hiện đại <br> 
        dành cho giảng viên Học viện Nông Nghiệp Việt Nam</p>
    </body>
    """, unsafe_allow_html = True)
    
with col2:
    with st.container(border = True):
        st.subheader("Đăng nhập hệ thống", text_alignment = "center")
        email = st.text_input("Email:")
        password = st.text_input("Password:", type = "password")
        sign_in = st.button("Đăng nhập", width="stretch")
        st.markdown("---")
        sign_up = st.button("Đăng ký", width="stretch")
    
def signin(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role FROM Users
        WHERE email = ? AND password = ?
    """, (email, password))

    role = cursor.fetchone()
    conn.close()

    return role is not None

if sign_in:
    if signin(email, password) == 0:
        st.switch_page("pages/dataviewer.py")
    elif signin(email, password) == 1: 
        st.switch_page("pages/camera.py")
    else: st.error("Người dùng không tồn tại")

if sign_up:
    st.switch_page("pages/sign_up.py")
