import pandas as pd
import streamlit as st
from src.database_query import notifications as db
from view.component.report_list import render_request_list
from src.services.load_report_record import _load_records

st.set_page_config(layout="wide", page_title="Biên bản ca thi", page_icon=":material/description:")

st.markdown("""
<style>
.block-container {padding-top:1.5rem; padding-bottom:1rem; max-width:100%;}
.page-heading h1 {font-size:1.65rem; margin:0; color:var(--text-color);}
.page-subtitle {color:var(--secondary-text-color); margin:.25rem 0 1.2rem 0; font-size:.92rem;}
div[data-testid="stDataFrame"] {width:100%;}
</style>
""", unsafe_allow_html=True)


st.markdown('<div class="page-heading"><h1>Biên bản ca thi</h1></div>', unsafe_allow_html=True)
st.markdown('<p class="page-subtitle">Tra cứu biên bản, lọc theo trạng thái và gửi biên bản cho quản trị viên.</p>', unsafe_allow_html=True)

left, right = st.columns([5, 1.5], vertical_alignment="center")

@st.dialog("Gửi biên bản ca thi", width="large")
def field_dialog():
    with st.form("field_report_form", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            mon_thi = st.text_input("Môn thi", value="Tin học đại cương")
        with c2:
            phong_thi = st.text_input("Phòng thi", value="Giảng đường Nguyễn Đăng - ND.202")
        ghi_chu = st.text_area(
            "Ghi chú giáo viên",
            value="Danh sách vi phạm do giáo viên ghi nhận và xác nhận trong ca thi.",
            height=130,
        )
        submitted = st.form_submit_button("Gửi biên bản cho quản trị viên", type="primary", use_container_width=True)
    if submitted:
        if not mon_thi.strip() or not phong_thi.strip():
            st.warning("Vui lòng nhập môn thi và phòng thi.")
        elif "professor_id" not in st.session_state:
            st.error("Không tìm thấy thông tin tài khoản đang đăng nhập.")
        else:
            try:
                db.create_request(
                    st.session_state["professor_id"],
                    db.REQUEST_FIELD_REPORT,
                    {"mon_thi": mon_thi.strip(), "phong_thi": phong_thi.strip(), "ghi_chu": ghi_chu.strip()},
                )
                st.success("Đã gửi biên bản. Quản trị viên sẽ nhận được thông báo.")
                st.rerun()
            except Exception as exc:
                st.error(f"Không gửi được biên bản: {exc}")

with left:
    st.markdown("### Danh sách biên bản")
with right:
    if st.button("＋ Tạo biên bản", type="primary", use_container_width=True, key="open_field_dialog"):
        field_dialog()


frame = _load_records("field")
render_request_list(
    frame,
    kind="field",
    key_prefix="field_report",
    height=520,
)
