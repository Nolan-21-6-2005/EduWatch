from datetime import date, datetime

import streamlit as st

from src.frontend.signup_request import request_signup
from view.component.auth_style import base_css, field_css

def show_sign_up():
    st.html(
        "<style>"
        + base_css()
        + field_css(
            ".st-key-signup-form",
            height=56,
            font_size=16,
            label_size=15,
            radius=13,
            button_height=58,
            button_font=18,
        )
        + "</style>"
    )

    with st.container(key="signup-shell"):
        left, right = st.columns([0.92, 1.45], gap="small")

        with left:
            st.html(
                """
                <div class="signup-banner">
                    <div class="signup-brand">
                        <span class="ew-icon" aria-hidden="true" translate="no">school</span>
                        <div class="signup-brand-text">EduWatch<br>VNUA</div>
                    </div>
                    <h1>Chào mừng đến<br>với hệ thống<br>AI quản trị học<br>tập và thi cử</h1>
                    <p>
                        Tham gia cộng đồng giảng viên tại Học viện Nông nghiệp Việt Nam để
                        quản lý và theo dõi tiến độ đào tạo hiệu quả hơn
                    </p>
                </div>
                """
            )

        with right:
            with st.container(key="signup-form"):
                st.html('<div class="signup-form-title">ĐĂNG KÝ TÀI KHOẢN</div>')

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
                    # Mặc định Streamlit chỉ cho chọn trong 10 năm gần đây -> mở rộng cho ngày sinh.
                    ngay_sinh = st.date_input(
                        "Ngày sinh",
                        value=None,
                        min_value=date(1940, 1, 1),
                        max_value=date.today(),
                        format="DD/MM/YYYY",
                    )
                with row2_right:
                    gioi_tinh = st.selectbox(
                        "Giới tính",
                        ["Chọn giới tính", "Nam", "Nữ", "Khác"],
                        index=0,
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

                sign_up = st.button("ĐĂNG KÝ", width="stretch", type="primary")
                back_login = st.button("QUAY LẠI ĐĂNG NHẬP", width="stretch", type="secondary")

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
