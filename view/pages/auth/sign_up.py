import streamlit as st
from datetime import datetime

from src.frontend.signup_request import request_signup


def show_sign_up():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stMainBlockContainer"] {
            max-width: 900px !important;
            margin: 0 auto !important;
            padding-top: 2.5rem !important;
        }
        .signup-title { text-align:center; color:#18212F; font-size:28px; font-weight:750; margin:5px 0 24px; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown('<div class="signup-title">Đăng ký tài khoản</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2, gap="medium")

        with c1:
            professor_id = st.text_input("Mã giảng viên", placeholder="GV000", icon=":material/badge:")
            ho_ten = st.text_input("Họ và tên", placeholder="Nguyễn Văn A", icon=":material/person:")
            gioi_tinh = st.selectbox("Giới tính", ["Nam", "Nữ", "Khác"])

        with c2:
            email = st.text_input("Email", placeholder="example@vnua.edu.vn", icon=":material/mail:")
            so_dien_thoai = st.text_input("Số điện thoại", placeholder="0987xxxxxx", icon=":material/call:")
            ngay_sinh = st.date_input("Ngày sinh")

        password = st.text_input("Mật khẩu", type="password", placeholder="••••••••", icon=":material/lock:")
        check_password = st.text_input("Nhập lại mật khẩu", type="password", placeholder="••••••••", icon=":material/verified_user:")
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        sign_up = st.button(":material/how_to_reg:  Đăng ký tài khoản", width="stretch", type="primary")
        back_login = st.button(":material/login:  Quay lại đăng nhập", width="stretch")

    if sign_up:
        if password != check_password:
            st.error("Mật khẩu không khớp")
            return
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = 0
        role = -1
        anh_dai_dien = "data_model/avatars/default.png"
        request_signup(
            professor_id, role, password, ho_ten, ngay_sinh, gioi_tinh,
            email, so_dien_thoai, anh_dai_dien, created_at, status,
        )

    if back_login:
        st.switch_page("view/pages/auth/sign_in.py")


show_sign_up()
