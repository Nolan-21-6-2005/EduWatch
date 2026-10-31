import inspect
import pandas as pd
import streamlit as st
import utils.config as cfg
from src.database_query import notifications as db
from view.component.admin_table import render_admin_table
from utils.helper import _find_col, _format_status
st.set_page_config(layout="wide", page_title="Báo cáo sự cố", page_icon=":material/report_problem:")


def _load_records(kind: str) -> pd.DataFrame:
    user_code = st.session_state.get("professor_id")

    if not user_code:
        return pd.DataFrame()

    if kind == "issue":
        records = db.get_incident_requests(user_code)
    elif kind == "field":
        records = db.get_field_report_requests(user_code)
    else:
        return pd.DataFrame()

    return pd.DataFrame(records)
    

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
search_col, status_col, type_col = st.columns([3, 1.2, 1.5], vertical_alignment="bottom")
with search_col:
    date_range = st.date_input(
        "KHOẢNG NGÀY",
        value=(cfg.start_date, cfg.end_date),
        format="DD/MM/YYYY",
        key="log_date_range",
    )
with status_col:
    status_filter = st.selectbox("Trạng thái", ["Tất cả", "Chờ xử lý", "Đang xử lý", "Đã xử lý"], default="Tất cả", key="issue_status_filter", width="stretch")
with type_col:
    types = ["Tất cả"]
    if not frame.empty:
        type_col_name = _find_col(frame, {"loai_su_co", "issue_type", "title", "subject", "loai"})
        if type_col_name:
            types += sorted(frame[type_col_name].dropna().astype(str).unique().tolist())
    type_filter = st.selectbox("Loại sự cố", types, key="issue_type_filter")

if not frame.empty:
    status_col_name = _find_col(frame, {"status", "trang_thai", "trang_thai_xu_ly", "state"})
    if status_col_name:
        frame["_Trạng thái"] = frame[status_col_name].map(_format_status)
        if status_filter != "Tất cả":
            frame = frame[frame["_Trạng thái"] == status_filter]
    if type_filter != "Tất cả":
        type_col_name = _find_col(frame, {"loai_su_co", "issue_type", "title", "subject", "loai"})
        if type_col_name:
            frame = frame[frame[type_col_name].astype(str) == type_filter]
    if query.strip():
        mask = frame.astype(str).apply(lambda col: col.str.contains(query.strip(), case=False, na=False)).any(axis=1)
        frame = frame[mask]
    # Ưu tiên các cột dễ đọc nếu tồn tại.
    display = frame.drop(columns=["_Trạng thái"], errors="ignore").copy()
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
        "issue_reports",
        table_data,
        height=520,
    )
    st.caption(f"{len(frame)} báo cáo phù hợp")
else:
    st.info("Chưa có dữ liệu lịch sử để hiển thị. Cần kết nối hàm truy vấn danh sách yêu cầu trong `src.database_query.notifications`; trang hiện chỉ có sẵn hàm tạo yêu cầu.")
