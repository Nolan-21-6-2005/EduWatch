import streamlit as st
import sqlite3
import sys
import requests
from pathlib import Path


def show_sign_in():
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("EduWatch VNUA")
        st.markdown(
            """
        <header>
            <h2>Kiến tạo tương lai <br> số hóa giáo dục</h2>
        </header>
        <body>
            <p>Hệ thống giám sát và quản lý đào tạo hiện đại <br> 
            dành cho giảng viên Học viện Nông Nghiệp Việt Nam</p>
        </body>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        with st.container(border=True):
            st.subheader("Đăng nhập hệ thống", text_alignment="center")
            email = st.text_input("Email:")
            password = st.text_input("Password:", type="password")
            sign_in = st.button("Đăng nhập", width="stretch")
            sign_up = st.button("Đăng ký", width="stretch")

    if sign_in:
        response = requests.post(
            "http://localhost:8000/login", json={"email": email, "password": password}
        )

        data = response.json()
        if data["success"]:
            st.session_state["email"] = data["email"]
            st.session_state["page"] = "dashboard"
            st.rerun()
        else:
            st.error("Sai thông tin đăng nhập")
    if sign_up:
        st.session_state["page"] = "signup"
        st.rerun()
