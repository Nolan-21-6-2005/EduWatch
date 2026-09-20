import streamlit as st

from src.frontend.login_request import request_login


def show_sign_in():
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stMainBlockContainer"] {
            max-width: 1080px !important;
            margin: 0 auto !important;
            padding-top: 5rem !important;
        }
        .auth-brand { color:#2DBB6D; font-size:22px; font-weight:750; margin-bottom:18px; }
        .auth-copy h2 { font-size:36px !important; margin:0 0 14px !important; }
        .auth-copy p { color:#7B8794 !important; font-size:15px !important; line-height:1.7 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.2, 1], gap="large")

    with col1:
        st.markdown(
            """
            <div class="auth-copy">
                <div class="auth-brand">EduWatch VNUA</div>
                <h2>Kiến tạo tương lai<br>số hóa giáo dục</h2>
                <p>Hệ thống giám sát và quản lý đào tạo hiện đại dành cho giảng viên Học viện Nông nghiệp Việt Nam.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        with st.container(border=True):
            st.markdown(
                "<h3 style='text-align:center;margin:4px 0 22px;'>Đăng nhập hệ thống</h3>",
                unsafe_allow_html=True,
            )
            professor_id = st.text_input("Mã giảng viên", icon=":material/badge:")
            password = st.text_input("Mật khẩu", type="password", icon=":material/lock:")
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            sign_in = st.button("Đăng nhập", width="stretch", type="primary")
            sign_up = st.button("Đăng ký tài khoản", width="stretch")

    if sign_in:
        request_login(professor_id, password)

    if sign_up:
        st.switch_page("view/pages/auth/sign_up.py")


show_sign_in()
