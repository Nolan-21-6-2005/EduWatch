import streamlit as st

from src.frontend.login_request import request_login
from view.component.auth_style import base_css, cover_image_data_uri, field_css

def show_sign_in():
    st.html(
        "<style>"
        + base_css()
        + field_css(
            ".st-key-login-form",
            height=60,
            font_size=18,
            label_size=16,
            radius=14,
            button_height=64,
            button_font=20,
        )
        + "</style>"
    )

    with st.container(key="login-shell"):
        left, right = st.columns([1.08, 0.92], gap="small")

        # ----------------------------------------------------
        # CỘT TRÁI
        # ----------------------------------------------------
        with left:
            st.html(
                f"""
                <div class="login-banner">
                    <div class="login-brand">
                        <div class="login-brand-icon">
                            <span class="ew-icon" aria-hidden="true" translate="no">school</span>
                        </div>
                        <div class="login-brand-text">EduWatch VNUA</div>
                    </div>

                    <h1>
                        Kiến tạo tương lai<br>
                        <span class="green-text">số hóa giáo dục</span>
                    </h1>

                    <p class="login-banner-description">
                        Hệ thống giám sát và quản lý đào tạo hiện đại
                        dành cho giảng viên Học viện Nông nghiệp Việt Nam.
                    </p>

                    <img
                        class="login-media"
                        src="{cover_image_data_uri()}"
                        alt="Tòa nhà Trung tâm - Học viện Nông nghiệp Việt Nam"
                    >
                </div>
                """
            )

        # ----------------------------------------------------
        # CỘT PHẢI: THẺ ĐĂNG NHẬP
        # ----------------------------------------------------
        with right:
            with st.container(key="login-form"):
                st.html('<div class="login-form-title">ĐĂNG NHẬP HỆ THỐNG</div>')
                st.html('<div class="login-form-subtitle">Cổng thông tin Giám sát Đào tạo</div>')

                professor_id = st.text_input(
                    "Tên đăng nhập",
                    placeholder="Nhập mã số người dùng",
                    icon=":material/person:",
                )

                password = st.text_input(
                    "Mật khẩu",
                    type="password",
                    placeholder="••••••••",
                    icon=":material/lock:",
                )

                remember_col, forgot_col = st.columns([1, 1], gap="small")
                with remember_col:
                    st.checkbox("Ghi nhớ", value=False)
                with forgot_col:
                    st.html('<div class="login-forgot">Quên mật khẩu?</div>')

                sign_in = st.button("ĐĂNG NHẬP", width="stretch", type="primary")

                st.html(
                    """
                    <div class="login-divider">
                        <span class="login-divider-line"></span>
                        <span>HOẶC</span>
                        <span class="login-divider-line"></span>
                    </div>
                    """
                )

                sign_up = st.button("Tạo tài khoản mới", width="stretch", type="secondary")

    # ========================================================
    # HÀNH ĐỘNG
    # ========================================================

    if sign_in:
        request_login(professor_id, password)

    if sign_up:
        st.switch_page("view/pages/auth/sign_up.py")


show_sign_in()
