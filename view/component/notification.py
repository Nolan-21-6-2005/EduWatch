from __future__ import annotations
import re
import html
import streamlit as st
from datetime import datetime
from src.database_query import notifications as db

POLL_SECONDS = 10
BELL_KEY = "topbar_notifications"

_FIELDS = {
    db.REQUEST_FIELD_REPORT: [("mon_thi", "Môn thi"), ("phong_thi", "Phòng thi"),
                              ("ghi_chu", "Ghi chú giảng viên")],
    db.REQUEST_INCIDENT: [("toa_nha", "Tòa nhà"), ("phong", "Phòng"),
                          ("loai_su_co", "Loại sự cố"), ("mo_ta", "Mô tả sự cố")],
}
_REQUEST_NAMES = {db.REQUEST_FIELD_REPORT: "Biên bản ca thi", db.REQUEST_INCIDENT: "Báo cáo sự cố"}


def _user_id() -> int | None:
    return db.get_user_id(st.session_state.get("professor_id", ""))


def _fmt_time(value: str | None) -> str:
    try:
        return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime("%H:%M · %d/%m/%Y")
    except (TypeError, ValueError):
        return value or ""


def _md(text: str) -> str:
    return re.sub(r"([\\`*_{}\[\]<>#~|:$])", r"\\\1", text or "")


def _clip(text: str, n: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[: n - 1] + "…"


# ---------------------------------------------------------------- chuông
def notification_bell() -> None:
    """Gọi BÊN TRONG container topbar, thay cho nút chuông cũ."""
    user_id = _user_id()
    if user_id is None:
        st.button(":material/notifications:", key=BELL_KEY)
        return
    _bell(user_id)


@st.fragment(run_every=POLL_SECONDS)
def _bell(user_id: int) -> None:
    unread = db.get_unread_ids(user_id)
    is_open = st.session_state.get("notif_open", False)

    # Không đặt help= : tooltip sẽ đè lên hộp thông báo ngay bên dưới chuông.
    clicked = st.button(":material/notifications:", key=BELL_KEY)

    if clicked:
        st.session_state["notif_open"] = not is_open
        st.session_state["notif_new_ids"] = set() if is_open else set(unread)
        if not is_open:
            db.mark_read(user_id, unread)      # badge biến mất
        st.rerun()

    if unread and is_open:                      # đang mở mà có thông báo mới đến
        st.session_state["notif_new_ids"] = st.session_state.get("notif_new_ids", set()) | set(unread)
        db.mark_read(user_id, unread)
        st.rerun()

    if unread:
        label = "99+" if len(unread) > 99 else str(len(unread))
        st.markdown(f'<style>.st-key-{BELL_KEY}::after{{content:"{label}";}}</style>',
                    unsafe_allow_html=True)


# ---------------------------------------------------------- hộp danh sách
def _item_label(item: dict) -> str:
    if item["loai"] == db.NOTI_REQUEST_APPROVED:
        icon = "check_circle"
    elif item["loai_yeu_cau"] == db.REQUEST_INCIDENT:
        icon = "report_problem"
    else:
        icon = "description"
    meta = f":gray[{_fmt_time(item['created_at'])}]"
    if item["loai"] == db.NOTI_NEW_REQUEST and item["trang_thai"] == db.STATUS_APPROVED:
        meta += "  ·  :green[Đã duyệt]"
    return (f":material/{icon}:  **{_md(item['tieu_de'])}**  \n"
            f"{_md(_clip(item['noi_dung'], 80))}  \n{meta}")


def notification_panel() -> None:
    """Gọi SAU container topbar."""
    flash = st.session_state.pop("notif_flash", None)
    if flash:
        st.toast(flash, icon=":material/check_circle:")

    if not st.session_state.get("notif_open"):
        return
    user_id = _user_id()
    if user_id is None:
        return

    items = db.list_notifications(user_id)
    new_ids = st.session_state.get("notif_new_ids", set())
    opened_id = None

    with st.container(key="ew_notif_panel"):
        with st.container(key="ew_notif_head", horizontal=True, vertical_alignment="center"):
            st.html('<div class="ew-noti-title">Thông báo</div>')
            if st.button(":material/close:", key="notif_close", type="tertiary"):
                st.session_state["notif_open"] = False
                st.session_state["notif_new_ids"] = set()
                st.rerun()
        if not items:
            st.caption("Chưa có thông báo nào.")
        for item in items:
            prefix = "notif_new_" if item["id"] in new_ids else "notif_"
            if st.button(_item_label(item), key=f"{prefix}{item['id']}", width="stretch"):
                opened_id = item["id"]

    if opened_id is not None:
        _detail_dialog(user_id, opened_id)


# ------------------------------------------------------------- chi tiết
def _status_badge(status: int | None) -> str:
    if status == db.STATUS_APPROVED:
        return '<span class="ew-noti-badge approved">Đã duyệt</span>'
    return '<span class="ew-noti-badge pending">Chờ duyệt</span>'


@st.dialog("Chi tiết thông báo", width="medium")
def _detail_dialog(user_id: int, notification_id: int) -> None:
    item = db.get_notification(user_id, notification_id)
    if item is None:
        st.warning("Thông báo này không còn tồn tại.")
        return
    if item["loai_yeu_cau"] is None:
        st.markdown(f"**{item['tieu_de']}**")
        st.write(item["noi_dung"])
        return

    is_admin = st.session_state.get("role") == 0
    esc = html.escape
    rows = [("Loại yêu cầu", esc(_REQUEST_NAMES.get(item["loai_yeu_cau"], "Yêu cầu")))]
    if is_admin:
        role = db.ROLE_LABELS.get(item["sender_role"], "")
        rows.append(("Người gửi", esc(f"{item['sender_name']} ({item['sender_code']}) · {role}")))
    rows.append(("Thời gian gửi", esc(_fmt_time(item["request_created_at"]))))
    for key, label in _FIELDS.get(item["loai_yeu_cau"], []):
        rows.append((label, esc(str(item["data"].get(key) or "—"))))
    rows.append(("Trạng thái", _status_badge(item["trang_thai"])))

    st.markdown(f"**{item['tieu_de']}**")
    st.caption(item["noi_dung"])
    st.html('<div class="ew-noti-detail">'
            + "".join(f'<div class="k">{k}</div><div class="v">{v}</div>' for k, v in rows)
            + "</div>")

    can_approve = (is_admin and item["loai"] == db.NOTI_NEW_REQUEST
                   and item["trang_thai"] == db.STATUS_PENDING)
    if can_approve and st.button(":material/check:  Duyệt yêu cầu",
                                 key=f"approve_{item['request_id']}",
                                 type="primary", width="stretch"):
        try:
            done = db.approve_request(item["request_id"], st.session_state["professor_id"])
        except PermissionError as exc:
            st.error(str(exc))
            return
        st.session_state["notif_flash"] = (
            "Đã duyệt yêu cầu và gửi thông báo cho người gửi." if done
            else "Yêu cầu này đã được duyệt trước đó.")
        st.rerun()
