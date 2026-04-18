import streamlit as st
import sqlite3
import re
import sys
import string
import collections
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "model" / "database.db"

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("EduWatch VNUA")
    st.markdown("""
    <header>
        <h2>Chúc mừng đến với hệ thống <br> AI quản trị số học tập</h2>
    </header>
    <body>
        <p>Tham gia cộng đồng giảng viên tại <br> 
        học viện Nông Nghiệp Việt Nam để <br> 
        quản lý và theo dõi tiến độ đào tạo <br> 
        hiệu quả hơn</p>
    </body>
    """, unsafe_allow_html = True)
with col2:
    st.subheader("Đăng ký tài khoản")
    c1, c2 = st.columns([1, 1])
    with c1:
        username = st.text_input("Username:")
        gender = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"])
        date = st.date_input("Ngày sinh")
    with c2:
        email = st.text_input("Email")
        phone = st.text_input("Số điện thoại")
        password = st.text_input("Password:", type = "password")
        check_password = st.text_input("Retype password:", type = "password")
        role = st.selectbox(
            "Vai trò:",
        ("Professor", "Supervisory", "Admin"),
        )
    sign_up = st.button("Đăng ký tài khoản")

def is_strong_password(password):
    return (
        len(password) >= 8 and
        re.search(r"[A-Z]", password) and      # chữ hoa
        re.search(r"[a-z]", password) and      # chữ thường
        re.search(r"[0-9]", password) and      # số
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)  # ký tự đặc biệt
    )

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
    
    
if sign_up:
    if signup(username, password, check_password):
        st.switch_page("pages/sign_in.py")
    else:
        st.error("Sai tên đăng nhập hoặc mật khẩu không đạt yêu cầu")
