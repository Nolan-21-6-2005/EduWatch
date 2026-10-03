from __future__ import annotations

from html import escape

import streamlit as st

from src.frontend.profile_service import (
    file_to_data_uri,
    get_user_by_code,
    get_user_by_id,
    phone_exists,
    resolve_avatar_path,
    role_name,
    save_avatar,
    update_password,
    update_profile_contact,
    verify_password,
)


def _get_logged_in_user() -> dict | None:
    user_id = st.session_state.get("user_id")
    if user_id:
        user = get_user_by_id(int(user_id))
        if user:
            return user

    professor_id = str(st.session_state.get("professor_id", "")).strip()
    if professor_id:
        return get_user_by_code(professor_id)

    return None


def _profile_field(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="ew-profile-field">
            <div class="ew-profile-field-label">{escape(label)}</div>
            <div class="ew-profile-field-value">{escape(value)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )



user = _get_logged_in_user()

if not user:
    st.error("Không tìm thấy thông tin người dùng. Vui lòng đăng nhập lại.")


user_id = int(user["id"])
user_code = str(user.get("ma_giang_vien") or "")
user_name = str(user.get("ho_ten") or "")
user_email = str(user.get("email") or "")
user_role = role_name(int(user.get("role") or -1))
user_status = "Hoạt động" if int(user.get("status") or 0) == 1 else "Đã khóa"
avatar_uri = file_to_data_uri(resolve_avatar_path(user.get("anh_dai_dien")))

st.markdown('<div class="ew-profile-page"></div>', unsafe_allow_html=True)
st.markdown(
    """
    <div class="ew-profile-title">Hồ sơ cá nhân</div>
    <div class="ew-profile-subtitle">
        Quản lý ảnh đại diện, số điện thoại và mật khẩu đăng nhập.
        Các thông tin định danh chỉ được xem.
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="ew-profile-card-marker"></div>', unsafe_allow_html=True)
with st.container(border=True):
    left, right = st.columns([0.42, 0.58], gap="large", vertical_alignment="top")

    with left:
        avatar_html = (
            f'<img class="ew-profile-avatar" src="{avatar_uri}" alt="avatar">'
            if avatar_uri
            else '<div class="ew-profile-avatar ew-profile-avatar-fallback">👤</div>'
        )

        st.markdown(
            f"""
            <div class="ew-profile-left">
                {avatar_html}
                <div class="ew-profile-name">{escape(user_name)}</div>
                <div class="ew-profile-code">{escape(user_code)}</div>
                <span class="ew-profile-role">{escape(user_role)}</span>
            </div>

            <div class="ew-profile-upload-title">
                <div>
                    <div>Đổi ảnh đại diện</div>
                    <div class="ew-profile-upload-note">JPG, PNG, WEBP</div>
                </div>
                <div class="ew-profile-upload-plus">+</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        uploaded = st.file_uploader(
            "Đổi ảnh đại diện",
            type=["jpg", "jpeg", "png", "webp"],
            key="profile_avatar",
            label_visibility="collapsed",
        )

    with right:
        _profile_field("Mã người dùng", user_code)
        _profile_field("Họ tên", user_name)
        _profile_field("Email", user_email or "--")
        _profile_field("Vai trò", user_role)
        _profile_field("Trạng thái tài khoản", user_status)

        st.markdown(
            '<div class="ew-profile-input-label">Số điện thoại</div>',
            unsafe_allow_html=True,
        )
        phone = st.text_input(
            "Số điện thoại",
            value=user.get("so_dien_thoai") or "",
            key="profile_phone",
            label_visibility="collapsed",
        )

        if st.button(
            "LƯU THAY ĐỔI",
            key="profile_save",
            type="primary",
        ):
            cleaned_phone = phone.strip()

            if cleaned_phone and phone_exists(cleaned_phone, user_id):
                st.error("Số điện thoại này đã được tài khoản khác sử dụng.")
            else:
                avatar_value = user.get("anh_dai_dien")

                if uploaded is not None:
                    try:
                        avatar_value = save_avatar(uploaded, user_code or str(user_id))
                    except ValueError as exc:
                        st.error(str(exc))

                updated = update_profile_contact(
                    user_id,
                    cleaned_phone,
                    avatar_value,
                )

                if updated:
                    # Duy trì session hiện tại, chỉ refresh dữ liệu profile.
                    st.session_state["profile_user"] = updated
                    st.success("Đã cập nhật hồ sơ.")
                    st.rerun()

st.markdown('<div class="ew-profile-password-marker"></div>', unsafe_allow_html=True)
with st.container(border=True):
    st.markdown(
        '<div class="ew-profile-section-title">Đổi mật khẩu</div>',
        unsafe_allow_html=True,
    )

    with st.form("profile_password_form"):
        old_password = st.text_input(
            "Mật khẩu hiện tại",
            type="password",
        )
        new_password = st.text_input(
            "Mật khẩu mới",
            type="password",
        )
        confirm_password = st.text_input(
            "Nhập lại mật khẩu mới",
            type="password",
        )

        submitted = st.form_submit_button(
            "CẬP NHẬT MẬT KHẨU",
        )

        if submitted:
            if not verify_password(user_id, old_password):
                st.error("Mật khẩu hiện tại không đúng.")
            elif len(new_password) < 6:
                st.error("Mật khẩu mới cần tối thiểu 6 ký tự.")
            elif new_password != confirm_password:
                st.error("Mật khẩu nhập lại không khớp.")
            elif old_password == new_password:
                st.error("Mật khẩu mới phải khác mật khẩu hiện tại.")
            else:
                update_password(user_id, new_password)
                st.success("Đã đổi mật khẩu.")
