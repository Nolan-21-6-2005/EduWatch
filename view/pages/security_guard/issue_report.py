import pandas as pd
import streamlit as st
from src.database_query import notifications as db
from view.component.report_list import render_request_list
from src.services.load_report_record import _load_records

st.set_page_config(layout="wide", page_title="Báo cáo sự cố", page_icon=":material/report_problem:")
    

st.markdown('<div class="page-heading"><h1>Báo cáo sự cố</h1></div>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Gửi yêu cầu hỗ trợ kỹ thuật và theo dõi trạng thái xử lý sự cố.</p>', unsafe_allow_html=True)

top_left, top_right = st.columns([5, 1.25], vertical_alignment="center")
with top_left:
    st.markdown("### Danh sách báo cáo")
with top_right:
    if "professor_id" not in st.session_state:
        st.warning("Phiên đăng nhập chưa có professor_id.")

@st.dialog("Gửi báo cáo sự cố", width="large")
def issue_dialog():
    with st.form("issue_report_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            toa_nha = st.selectbox("Tòa nhà", ["Giảng đường A", "Giảng đường B", "Giảng đường Nguyễn Đăng"], key="issue_building")
        with c2:
            phong = st.selectbox("Phòng", ["ND.202", "ND.206", "ND.102"], key="issue_room")
        loai_su_co = st.text_input("Loại sự cố", placeholder="Ví dụ: Camera offline, mất nguồn...")
        mo_ta = st.text_area("Mô tả sự cố", placeholder="Mô tả chi tiết tình trạng sự cố kỹ thuật...", height=130)
        submitted = st.form_submit_button("Gửi báo cáo", type="primary", use_container_width=True)
    if submitted:
        if not loai_su_co.strip() or not mo_ta.strip():
            st.warning("Vui lòng nhập loại sự cố và mô tả sự cố.")
        elif "professor_id" not in st.session_state:
            st.error("Không tìm thấy thông tin tài khoản đang đăng nhập.")
        else:
            try:
                db.create_request(
                    st.session_state["professor_id"],
                    db.REQUEST_INCIDENT,
                    {"toa_nha": toa_nha, "phong": phong, "loai_su_co": loai_su_co.strip(), "mo_ta": mo_ta.strip()},
                )
                st.session_state["issue_report_sent"] = True
                st.success("Đã gửi báo cáo. Quản trị viên sẽ nhận được thông báo.")
                st.rerun()
            except Exception as exc:
                st.error(f"Không gửi được báo cáo: {exc}")

with top_right:
    if st.button("＋ Báo cáo sự cố", type="primary", use_container_width=True, key="open_issue_dialog"):
        issue_dialog()

frame = _load_records("issue")
render_request_list(
    frame,
    kind="issue",
    key_prefix="issue_report",
    height=520,
)
