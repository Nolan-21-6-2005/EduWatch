import streamlit as st
import sqlite3
import sys
import requests
from pathlib import Path


def show_sign_in():
    # --- CAN THIỆP TRỰC TIẾP VÀO HỆ THỐNG STREAMLIT ĐỂ ÉP CO TRANG ---
    st.markdown("""
        <style>
        /* Nhắm thẳng vào container gốc của Streamlit để ép độ rộng */
        [data-testid="stMainBlockContainer"] {
            max-width: 950px !important;
            margin: 0 auto !important;
            padding-top: 7rem !important; /* Đẩy nội dung xuống giữa màn hình theo chiều dọc */
        }
        
        /* Tùy chỉnh font chữ phần giới thiệu bên trái */
        .intro-section h2 {
            font-size: 34px !important;
            font-weight: 700 !important;
            line-height: 1.4 !important;
            color: #FFFFFF !important;
            margin-bottom: 15px;
        }
        
        .intro-section p {
            font-size: 15px !important;
            color: #A0AEC0 !important;
            line-height: 1.6 !important;
        }
        
        /* Làm đẹp khung viền container đăng nhập */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 12px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Thiết lập layout chia cột bên trong vùng đã co cụm
    col1, col2 = st.columns([1.2, 1], gap="large")
    
    with col1:
        st.markdown(
            """
            <div class="intro-section">
                <h3 style="color: #2CBD6C; font-weight: 700; margin-bottom: 20px; font-size: 22px;">EduWatch VNUA</h3>
                <h2>Kiến tạo tương lai <br> số hóa giáo dục</h2>
                <p style="margin-top: 20px;">Hệ thống giám sát và quản lý đào tạo hiện đại <br> 
                dành cho giảng viên Học viện Nông Nghiệp Việt Nam</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        # Sử dụng border=True tạo khung hộp đăng nhập
        with st.container(border=True):
            st.markdown("<h3 style='text-align: center; color: white; margin-bottom: 25px; font-weight: 600;'>Đăng nhập hệ thống</h3>", unsafe_allow_html=True)
            
            email = st.text_input("Email:")
            password = st.text_input("Password:", type="password")
            
            st.write("") # Khoảng cách nhỏ
            
            # Các nút bấm kéo giãn vừa khung
            sign_in = st.button("Đăng nhập", use_container_width=True, type="primary")
            sign_up = st.button("Đăng ký", use_container_width=True)

    # --- XỬ LÝ LOGIC SỰ KIỆN ---
    if sign_in:
        try:
            response = requests.post(
                "http://localhost:8000/login", json={"email": email, "password": password}
            )
            data = response.json()
            if data["success"]:
                st.session_state["email"] = data["email"]
                st.session_state["page"] = "dashboard"
                st.session_state["role"] = data["role"]
                st.rerun()
            else:
                st.error("Sai thông tin đăng nhập")
        except Exception as e:
            st.error("Không thể kết nối đến Server dịch vụ Backend.")

    if sign_up:
        st.session_state["page"] = "signup"
        st.rerun()
