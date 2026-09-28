import streamlit as st
from datetime import datetime

from src.frontend.signup_request import request_signup


def show_sign_up():
    # Trang đăng ký là trang auth nên không dùng sidebar/header mặc định.
    st.markdown(
        """
        <style>
        header[data-testid="stHeader"] {
            display: none !important;
        }

        [data-testid="stSidebar"],
        [data-testid="stSidebarCollapsedControl"] {
            display: none !important;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1120px !important;
            margin: 0 auto !important;
            padding: 3.5rem 1.25rem 2.5rem !important;
        }

        .st-key-signup-shell {
            width: 100%;
            border-radius: 20px;
            margin: 10px;
            overflow: hidden;
            background: #ffffff;

            box-shadow:
                0 24px 60px rgba(34, 53, 44, 0.10),
                0 8px 24px rgba(34, 53, 44, 0.06);
        }

        .signup-banner {
            min-height: 650px;
            height: 100%;
            padding: 42px 40px;
            border-radius: 18px 0 0 18px;
            background: linear-gradient(145deg, #35bd73 0%, #0d9851 100%);
            color: #ffffff;
            position: relative;
            overflow: hidden;
        }

        .signup-banner::before,
        .signup-banner::after {
            content: "";
            position: absolute;
            border-radius: 999px;
            border: 18px solid rgba(255,255,255,.10);
            pointer-events: none;
        }

        .signup-banner::before {
            width: 260px;
            height: 260px;
            right: -145px;
            bottom: -105px;
        }

        .signup-banner::after {
            width: 115px;
            height: 115px;
            right: 35px;
            bottom: -65px;
            border-width: 12px;
        }

        .signup-brand {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 45px;
            position: relative;
            z-index: 1;
        }

        .signup-brand-icon {
            width: 42px;
            height: 42px;
            border: 3px solid #ffffff;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 23px;
            font-weight: 800;
            line-height: 1;
        }

        .signup-brand-text {
            font-size: 23px;
            line-height: 1.15;
            font-weight: 800;
            letter-spacing: -0.02em;
        }

        .signup-banner h1 {
            color: #ffffff !important;
            font-size: 38px !important;
            line-height: 1.18 !important;
            font-weight: 800 !important;
            letter-spacing: -0.03em !important;
            margin: 0 0 22px !important;
            position: relative;
            z-index: 1;
        }

        .signup-banner p {
            max-width: 430px;
            color: rgba(255,255,255,.82);
            font-size: 16px;
            line-height: 1.75;
            margin: 0;
            position: relative;
            z-index: 1;
        }

        .signup-form {
            min-height: 650px;
            height: 100%;
            padding: 54px 54px 42px;
            background: #ffffff;
            border-radius: 0 18px 18px 0;
        }

        .signup-form-title {
            color: #37463f;
            text-align: center;
            font-size: 30px;
            line-height: 1.2;
            font-weight: 800;
            letter-spacing: -0.03em;
            margin: 0 20px 36px;
        }

        .signup-form [data-testid="stWidgetLabel"] p {
            color: #536158 !important;
            font-size: 15px !important;
            font-weight: 650 !important;
        }

        .signup-form [data-baseweb="input"] > div,
        .signup-form [data-baseweb="select"] > div {
            background: #e3e5e4 !important;
            border: 1px solid #e3e5e4 !important;
            border-radius: 13px !important;
            min-height: 55px !important;
        }

        .signup-form [data-baseweb="input"] > div:focus-within,
        .signup-form [data-baseweb="select"] > div:focus-within {
            background: #eef8f2 !important;
            border-color: #48be7a !important;
            box-shadow: 0 0 0 3px rgba(45, 187, 109, .10) !important;
        }

        .signup-form [data-baseweb="input"] input,
        .signup-form [data-baseweb="select"] input {
            color: #26312b !important;
            font-size: 16px !important;
        }

        .signup-form [data-baseweb="select"] > div {
            padding-left: 10px !important;
        }

        .signup-form .stDateInput [data-baseweb="input"] > div {
            min-height: 55px !important;
        }

        .signup-form .stButton > button {
            min-height: 55px !important;
            border-radius: 13px !important;
            font-size: 17px !important;
            font-weight: 750 !important;
            letter-spacing: .01em;
        }

        .signup-form .stButton > button[kind="primary"] {
            background: #32bd73 !important;
            border-color: #32bd73 !important;
            color: #ffffff !important;
            box-shadow: 0 8px 18px rgba(45, 187, 109, .16) !important;
        }

        .signup-form .stButton > button[kind="secondary"] {
            border-color: #32bd73 !important;
            color: #25a960 !important;
            background: #ffffff !important;
        }

        .signup-form .stButton > button[kind="secondary"]:hover {
            background: #f1fbf5 !important;
            border-color: #25a960 !important;
        }

        .signup-form [data-testid="stHorizontalBlock"] {
            gap: 22px !important;
        }

        .signup-form .stButton {
            margin-top: 14px;
        }

        @media (max-width: 900px) {
            [data-testid="stMainBlockContainer"] {
                padding: 1.5rem .8rem 2rem !important;
            }

            .signup-banner,
            .signup-form {
                border-radius: 18px !important;
                min-height: auto;
            }

            .signup-banner {
                padding: 32px 28px;
            }

            .signup-form {
                padding: 36px 28px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.container(key="signup-shell"):
        left, right = st.columns([0.92, 1.45])

        with left:
            st.markdown(
                """
                <div class="signup-banner">
                    <div class="signup-brand">
                        <div class="signup-brand-icon">⌂</div>
                        <div class="signup-brand-text">EduWatch<br>VNUA</div>
                    </div>
                    <h1>Chào mừng đến<br>với hệ thống<br>AI quản trị học<br>tập và thi cử</h1>
                    <p>
                        Tham gia cộng đồng giảng viên tại Học viện Nông nghiệp Việt Nam để
                        quản lý và theo dõi tiến độ đào tạo hiệu quả hơn
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with right:
            with st.container(key="signup-form"):
                st.markdown(
                    '<div class="signup-form-title">ĐĂNG KÝ TÀI KHOẢN</div>',
                    unsafe_allow_html=True,
                )

                row1_left, row1_right = st.columns(2, gap="medium")
                with row1_left:
                    professor_id = st.text_input(
                        "Mã giảng viên",
                        placeholder="VD: GV12345",
                        icon=":material/badge:",
                    )
                with row1_right:
                    ho_ten = st.text_input(
                        "Họ và tên",
                        placeholder="Nguyễn Văn A",
                        icon=":material/person:",
                    )

                row2_left, row2_right = st.columns(2, gap="medium")
                with row2_left:
                    ngay_sinh = st.date_input(
                        "Ngày sinh",
                        value=None
                    )
                with row2_right:
                    gioi_tinh = st.selectbox(
                        "Giới tính",
                        ["Chọn giới tính", "Nam", "Nữ", "Khác"],
                        index=0
                    )

                row3_left, row3_right = st.columns(2, gap="medium")
                with row3_left:
                    email = st.text_input(
                        "Email",
                        placeholder="example@vnua.edu.vn",
                        icon=":material/mail:",
                    )
                with row3_right:
                    so_dien_thoai = st.text_input(
                        "Số điện thoại",
                        placeholder="0987xxxxxx",
                        icon=":material/call:",
                    )

                row4_left, row4_right = st.columns(2, gap="medium")
                with row4_left:
                    password = st.text_input(
                        "Mật khẩu",
                        type="password",
                        placeholder="••••••••",
                        icon=":material/lock:",
                    )
                with row4_right:
                    check_password = st.text_input(
                        "Nhập lại mật khẩu",
                        type="password",
                        placeholder="••••••••",
                        icon=":material/lock_reset:",
                    )

                sign_up = st.button(
                    "ĐĂNG KÝ",
                    width="stretch",
                    type="primary",
                )
                back_login = st.button(
                    "QUAY LẠI ĐĂNG NHẬP",
                    width="stretch",
                    type="secondary",
                )

    if sign_up:
        if not professor_id.strip() or not ho_ten.strip() or not email.strip():
            st.error("Vui lòng nhập đầy đủ mã giảng viên, họ tên và email.")
            return

        if gioi_tinh == "Chọn giới tính":
            st.error("Vui lòng chọn giới tính.")
            return

        if not ngay_sinh:
            st.error("Vui lòng chọn ngày sinh.")
            return

        if password != check_password:
            st.error("Mật khẩu không khớp.")
            return

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = 0
        role = -1
        anh_dai_dien = "data_model/avatars/default.png"

        request_signup(
            professor_id,
            role,
            password,
            ho_ten,
            ngay_sinh,
            gioi_tinh,
            email,
            so_dien_thoai,
            anh_dai_dien,
            created_at,
            status,
        )

    if back_login:
        st.switch_page("view/pages/auth/sign_in.py")


show_sign_up()
