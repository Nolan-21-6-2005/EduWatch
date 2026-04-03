import streamlit as st
import sqlite3
import sys

sys.path.append('/var/home/namson/Webdevelopment/model')
st.title("Đăng ký tài khoản")
username = st.text_input("Email:")
password = st.text_input("Password:", type = "password")
check_password = st.text_input("Retype password:", type = "password")
sign_up = st.button("Đăng ký tài khoản")

def signup(username, password, check_password):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    if password == check_password:
        cursor.execute("""
        INSERT INTO Users (username, password)
        VALUES (?, ?)
        """, (username, password))
        return True
    else: return False
    
    conn.commit()
    conn.close()

if sign_up:
    if signup(username, password, check_password):
        st.switch_page("pages/homepage.py")
    else:
        st.error("Sai thông tin")
