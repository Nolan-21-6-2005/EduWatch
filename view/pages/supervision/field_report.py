import pandas as pd
import streamlit as st
from src.database_query import notifications as db
from view.component.admin_table import render_admin_table
from utils.helper import _find_col, _format_status

st.set_page_config(layout="wide", page_title="Biên bản ca thi", page_icon=":material/description:")

st.markdown("""
<style>
.block-container {padding-top:1.5rem; padding-bottom:1rem; max-width:100%;}
.page-heading h1 {font-size:1.65rem; margin:0; color:var(--text-color);}
.page-subtitle {color:var(--secondary-text-color); margin:.25rem 0 1.2rem 0; font-size:.92rem;}
div[data-testid="stDataFrame"] {width:100%;}
</style>
""", unsafe_allow_html=True)



def _load_records() -> pd.DataFrame:
    user_code = st.session_state.get("professor_id")

    if not user_code:
        return pd.DataFrame()

    records = db.get_field_report_requests(user_code)
    return pd.DataFrame(records)


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


frame = _load_records()
search_col, status_col, subject_col = st.columns([1.7, 1.2, 1], vertical_alignment="bottom")
with search_col:
    query = st.text_input("Tìm kiếm", placeholder="Tìm theo môn thi, phòng thi, ghi chú...", key="field_search")
with status_col:
    status_filter = st.segmented_control("Trạng thái", ["Tất cả", "Chờ xử lý", "Đang xử lý", "Đã xử lý"], default="Tất cả", key="field_status_filter", width="stretch")
with subject_col:
    options = ["Tất cả"]
    if not frame.empty:
        subject_col_name = _find_col(frame, {"mon_thi", "subject", "course", "ten_mon"})
        if subject_col_name:
            options += sorted(frame[subject_col_name].dropna().astype(str).unique().tolist())
    subject_filter = st.selectbox("Môn thi", options, key="field_subject_filter")

if not frame.empty:
    status_col_name = _find_col(frame, {"status", "trang_thai", "trang_thai_xu_ly", "state"})
    if status_col_name:
        frame["_Trạng thái"] = frame[status_col_name].map(_format_status)
        if status_filter != "Tất cả":
            frame = frame[frame["_Trạng thái"] == status_filter]
    if subject_filter != "Tất cả":
        subject_col_name = _find_col(frame, {"mon_thi", "subject", "course", "ten_mon"})
        if subject_col_name:
            frame = frame[frame[subject_col_name].astype(str) == subject_filter]
    if query.strip():
        mask = frame.astype(str).apply(lambda col: col.str.contains(query.strip(), case=False, na=False)).any(axis=1)
        frame = frame[mask]
    table_data = []

    for _, row in frame.iterrows():
        report = row.get("request_data", {})
        if not isinstance(report, dict):
            report = {}

        table_data.append({
            "id": row.get("id", ""),
            "title": report.get("mon_thi", "Chưa xác định"),
            "room": report.get("phong_thi", "--"),
            "datetime_display": str(row.get("created_at", "--")),
            "sender": row.get("sender_name", "--"),
            "review_status": row.get("status", "pending"),
            "note": report.get("ghi_chu", ""),
        })

    render_admin_table(
        "field_reports",
        table_data,
        height=520,
    )
    st.caption(f"{len(frame)} biên bản phù hợp")
    csv = frame.to_csv(index=False).encode("utf-8-sig")
    st.download_button("Xuất danh sách CSV", data=csv, file_name="bien_ban_ca_thi.csv", mime="text/csv")
else:
    st.info("Chưa có dữ liệu lịch sử để hiển thị. Cần kết nối hàm truy vấn danh sách biên bản trong `src.database_query.notifications`; file hiện tại chỉ thể hiện hàm tạo yêu cầu.")
