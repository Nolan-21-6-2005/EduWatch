from __future__ import annotations

from contextlib import nullcontext
from datetime import datetime
from html import escape

import streamlit as st

from src.frontend.profile_service import (
    file_to_data_uri,
    phone_exists,
    resolve_avatar_path,
    role_name,
    save_avatar,
    update_password,
    update_profile_contact,
    verify_password,
)
from src.services.profile_service import _get_logged_in_user

def _fmt_date(value: str | None, fmt_in: str = "%Y-%m-%d") -> str:
    try:
        return datetime.strptime(str(value)[:19], fmt_in).strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return str(value or "")


user = _get_logged_in_user()
if not user:
    st.error("Không tìm thấy thông tin người dùng. Vui lòng đăng nhập lại.")
    st.stop()

user_id = int(user["id"])
user_code = str(user.get("ma_giang_vien") or "")
user_name = str(user.get("ho_ten") or "")
user_email = str(user.get("email") or "")
user_phone = str(user.get("so_dien_thoai") or "")
role_value = user.get("role")  # role 0 (quản trị) là giá trị hợp lệ, không dùng `or`
user_role = role_name(int(role_value) if role_value is not None else -1)
is_active = int(user.get("status") or 0) == 1
user_status = "Đang hoạt động" if is_active else "Đã khóa"
status_html = f'<span class="ew-status {"ok" if is_active else "off"}">{escape(user_status)}</span>'
avatar_uri = file_to_data_uri(resolve_avatar_path(user.get("anh_dai_dien")))

editing = st.session_state.get("profile_edit_open", False)

flash = st.session_state.pop("profile_flash", None)
if flash:
    st.toast(flash, icon=":material/check_circle:")


# ------------------------------------------------------------ đổi mật khẩu
@st.dialog("Đổi mật khẩu", width="small")
def password_dialog() -> None:
    with st.form("profile_password_form", border=False):
        old_password = st.text_input("Mật khẩu hiện tại", type="password")
        new_password = st.text_input("Mật khẩu mới", type="password")
        confirm_password = st.text_input("Nhập lại mật khẩu mới", type="password")
        submitted = st.form_submit_button("Cập nhật mật khẩu", type="primary", width="stretch")
    if not submitted:
        return
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
        st.session_state["profile_flash"] = "Đã đổi mật khẩu."
        st.rerun()  # đóng hộp thoại


# ------------------------------------------------------------ ô thông tin
def field(label: str, value: str, key: str, editable: bool = False, view_html: str | None = None):
    """Chế độ xem: ô HTML. Chế độ sửa: text_input cùng hình dạng (trường định danh bị khóa)."""
    if editing:
        return st.text_input(label, value=value, key=f"profile_f_{key}", disabled=not editable)
    shown = view_html or escape(value) or "—"
    st.html(f'<div class="ew-pf-label">{escape(label)}</div><div class="ew-pf-box">{shown}</div>')
    return value


def card(key: str, title: str):
    box = st.container(key=f"profile_card_{key}")
    with box:
        st.html(f'<div class="ew-pf-title">{escape(title)}</div>')
    return box


# ------------------------------------------------------------ giao diện
with st.container(key="ew_profile_page"):

    # ===== Header: avatar, tên, mã, vai trò, trạng thái, nút thao tác =====
    with st.container(key="profile_card_header"):
        with st.container(key="profile_header_top", horizontal=True, vertical_alignment="center"):
            with st.container(key="profile_avatar_box"):
                img = (
                    f'<img src="{avatar_uri}" alt="Ảnh đại diện">'
                    if avatar_uri
                    else '<div class="ew-pf-avatar-fallback">👤</div>'
                )
                st.html(
                    f'<div class="ew-pf-avatar">{img}'
                    f'<span class="ew-pf-avatar-cam"><span class="ew-pf-cam-icon">photo_camera</span><span>Đổi ảnh</span></span></div>'
                )
                avatar_file = st.file_uploader(
                    "Ảnh đại diện",
                    type=["jpg", "jpeg", "png", "webp"],
                    key=f"profile_avatar_up_{st.session_state.get('profile_avatar_n', 0)}",
                    label_visibility="collapsed",
                )

            st.html(
                '<div class="ew-pf-identity">'
                f'<div class="ew-pf-name">{escape(user_name)}</div>'
                f'<div class="ew-pf-code">Mã: <b>{escape(user_code)}</b></div>'
                f'<span class="ew-pf-tag">{escape(user_role)}</span>'
                '</div>'
            )
            st.html(status_html)

        with st.container(key="profile_header_actions", horizontal=True, vertical_alignment="center"):
            if st.button(
                "Đóng chỉnh sửa" if editing else "Chỉnh sửa thông tin",
                icon=":material/close:" if editing else ":material/edit:",
                key="profile_btn_edit",
            ):
                st.session_state["profile_edit_open"] = not editing
                st.rerun()
            if st.button("Đổi mật khẩu", icon=":material/lock:", key="profile_btn_password"):
                password_dialog()

    # Chọn ảnh xong: lưu ngay (giữ nguyên số điện thoại), đổi key uploader để reset
    if avatar_file is not None:
        try:
            avatar_value = save_avatar(avatar_file, user_code or str(user_id))
        except ValueError as exc:
            st.error(str(exc))
        else:
            update_profile_contact(user_id, user_phone, avatar_value)
            st.session_state["profile_avatar_n"] = st.session_state.get("profile_avatar_n", 0) + 1
            st.session_state["profile_flash"] = "Đã cập nhật ảnh đại diện."
            st.rerun()

    # ===== Các khối thông tin (ở chế độ sửa được bọc trong một form) =====
    with st.form("profile_form", border=False) if editing else nullcontext():

        with card("personal", "Thông tin cá nhân"):
            col_l, col_r = st.columns(2, gap="large")
            with col_l:
                field("Họ và tên", user_name, "name")
                field("Ngày sinh", _fmt_date(user.get("ngay_sinh")), "dob")
            with col_r:
                field("Mã người dùng", user_code, "code")
                field("Giới tính", str(user.get("gioi_tinh") or ""), "gender")

        with card("contact", "Thông tin liên hệ"):
            col_l, col_r = st.columns(2, gap="large")
            with col_l:
                field("Email", user_email, "email")
            with col_r:
                new_phone = field("Số điện thoại", user_phone, "phone", editable=True)

        with card("account", "Tài khoản"):
            col_l, col_r = st.columns(2, gap="large")
            with col_l:
                field("Vai trò", user_role, "role")
                field("Ngày tạo", _fmt_date(user.get("created_at"), "%Y-%m-%d %H:%M:%S"), "created")
            with col_r:
                field("Trạng thái hoạt động", user_status, "status", view_html=status_html)

        if editing:
            with st.container(key="profile_form_actions", horizontal=True):
                cancelled = st.form_submit_button("Hủy", key="profile_btn_cancel", icon=":material/close:")
                saved = st.form_submit_button("Lưu thay đổi", type="primary", icon=":material/check:")

    if editing and cancelled:
        st.session_state["profile_edit_open"] = False
        st.rerun()

    if editing and saved:
        cleaned_phone = new_phone.strip()
        if cleaned_phone and phone_exists(cleaned_phone, user_id):
            st.error("Số điện thoại này đã được tài khoản khác sử dụng.")
        else:
            update_profile_contact(user_id, cleaned_phone)
            st.session_state["profile_edit_open"] = False
            st.session_state["profile_flash"] = "Đã cập nhật thông tin cá nhân."
            st.rerun()
