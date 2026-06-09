import streamlit as st
from datetime import datetime
from src.frontend.signup_request import request_signup

def show_sign_up():
    st.markdown("""
        <style>

        .stApp {
            background-color: #0f1117;
        }
        
        /* =========================
           MAIN CONTAINER
        ========================= */
        [data-testid="stMainBlockContainer"] {
            max-width: 800px !important;
            margin: 0 auto !important;
            padding-top: 5rem !important;
        }

        /* =========================
           LEFT INTRO
        ========================= */
        .intro-section h2 {
            font-size: 36px !important;
            font-weight: 700 !important;
            line-height: 1.35 !important;
            color: #FFFFFF !important;
            margin-bottom: 18px;
        }

        .intro-section p {
            font-size: 15px !important;
            color: #94A3B8 !important;
            line-height: 1.7 !important;
        }

        .intro-logo {
            color: #22C55E;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 28px;
        }

        /* =========================
           CARD
        ========================= */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #1c1f26 !important;
            border: 1px solid #2d3748 !important;
            border-radius: 18px !important;
            padding: 12px !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.35);
        }

        .signup-title {
            text-align: center;
            color: white;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 28px;
        }

        /* =========================
           BUTTON
        ========================= */
        .stButton button {
            height: 50px;
            border-radius: 12px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            border: none !important;
            transition: 0.2s ease;
        }

        .stButton button:hover {
            transform: translateY(-1px);
        }
        </style>
    """,unsafe_allow_html=True,)

    # =========================
    # LEFT INTRO
    # =========================
    with st.container(border=True):
        st.markdown(
            """
            <div class="signup-title">
                Đăng ký tài khoản
            </div>
            """,
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns(2)
        
        with c1:
            professor_id = st.text_input(
                "Mã giảng viên",
                placeholder="GV000",
                icon=":material/badge:"
            )

            ho_ten = st.text_input(
                "Họ và tên",
                placeholder="Nguyễn Văn A",
                icon=":material/person:"
            )

            gioi_tinh = st.selectbox(
                "Giới tính",
                ["Nam", "Nữ", "Khác"]
            )

        with c2:
            email = st.text_input(
                "Email",
                placeholder="example@vnua.edu.vn",
                icon=":material/mail:"
            )

            so_dien_thoai = st.text_input(
                "Số điện thoại",
                placeholder="0987xxxxxx",
                icon=":material/call:"
            )

            ngay_sinh = st.date_input(
                "Ngày sinh",
            )

        password = st.text_input(
            "Mật khẩu",
            type="password",
            placeholder="••••••••",
            icon=":material/lock:"
        )

        check_password = st.text_input(
            "Nhập lại mật khẩu",
            type="password",
            placeholder="••••••••",
            icon=":material/verified_user:"
        )

        st.write("")

        sign_up = st.button(
            ":material/how_to_reg: Đăng ký tài khoản",
            width="stretch",
            type="primary"
        )

        back_login = st.button(
            ":material/login: Quay lại đăng nhập",
            width="stretch"
        )

    # =========================
    # SIGNUP LOGIC
    # =========================
    if sign_up:
        if password != check_password:
            st.error("Mật khẩu không khớp")
            return
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = 0
        role = -1
        anh_dai_dien = "data_model/avatars/default.png"
        
        request_signup(professor_id, role, password, 
                       ho_ten, ngay_sinh, gioi_tinh, 
                       email, so_dien_thoai, anh_dai_dien, 
                       created_at, status)

    # =========================
    # BACK LOGIN
    # =========================
    if back_login:
        st.session_state["page"] = "login"
        st.rerun()
