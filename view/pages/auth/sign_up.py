import streamlit as st
import string
import collections
import requests


def show_sign_up():
    col1, col2 = st.columns([1, 1])
    st.subheader("Đăng ký tài khoản")
    c1, c2 = st.columns([1, 1])
    with c1:
        username = st.text_input("Username:")
        gender = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"])
        date = st.date_input("Ngày sinh")
    with c2:
        email = st.text_input("Email")
        phone = st.text_input("Số điện thoại")
    password = st.text_input("Password:", type="password")
    check_password = st.text_input("Retype password:", type="password")
    sign_up = st.button("Đăng ký tài khoản")
    if sign_up:
        response = requests.post(
            "http://localhost:8000/signup", json={"email": email, "password": password}
        )
        data = response.json()
        if data["success"]:
            st.session_state["page"] = "login"
            st.rerun()
        else:
            st.error("So dien thoai da ton tai")
