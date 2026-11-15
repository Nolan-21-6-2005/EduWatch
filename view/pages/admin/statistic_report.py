import streamlit as st
from datetime import date

import src.database_query.violation_logs as vldb

import utils.config as cfg
from utils.helper import date_range_bounds
from view.component.metric import kpi_metric
from view.component.violation_bar_chart import render_violation_bar_chart
from view.component.report_list import render_request_list
from src.services.load_report_record import _load_records

st.set_page_config(
    page_title="Thống kê báo cáo",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# 1. CHỌN KHOẢNG THỜI GIAN (TÙY CHỌN)
# =========================================================
col1, col2 = st.columns([3,1])
with col1:
    with st.container(horizontal=True, horizontal_alignment="left", vertical_alignment="bottom"):
        st.header("Thống kê báo cáo")
with col2:
    with st.container(horizontal=True, horizontal_alignment="right", vertical_alignment="center"):
        # Mặc định lọc dữ liệu trong ngày hiện tại.
        date_range = st.date_input(
            "KHOẢNG NGÀY",
            value=(date.today(), date.today()),
            format="DD/MM/YYYY",
            key="stats_date_range",
            label_visibility="collapsed",
        )

start_date_value, end_date_value = date_range_bounds(date_range)
start_date_str = start_date_value.strftime("%Y-%m-%d") if start_date_value else None
end_date_str = end_date_value.strftime("%Y-%m-%d") if end_date_value else None


# =========================================================
# 2. LẤY DỮ LIỆU TỪ DATABASE THEO KHOẢNG THỜI GIAN
# =========================================================

study_room_kpis = vldb.get_violation_report_kpis(
    start_date=start_date_str,
    end_date=end_date_str,
    session=cfg.SESSION_MAP["Phòng thường"]
)

exam_room_kpis = vldb.get_violation_report_kpis(
    start_date=start_date_str,
    end_date=end_date_str,
    session=cfg.SESSION_MAP["Phòng thi"]
)

# =========================================================
# 4. KPI
# =========================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")

with kpi1:
    kpi_metric(
        study_room_kpis["confirmed"], 
        "Vi phạm phòng thường", 
        "Tổng vi phạm ở phòng thường",
        "green"
    )

with kpi2:
    kpi_metric(
        study_room_kpis["loai_vi_pham"], 
        "Vi phạm phổ biến phòng thường",
        "Loại vi phạm phổ biến ở phòng thường" ,
        "green"
    )
with kpi3:
    kpi_metric(
        exam_room_kpis["confirmed"], 
        "Vi phạm phòng thi", 
        "Tổng vi phạm ở phòng thi",
        "green"
    )

with kpi4:
    kpi_metric(
        exam_room_kpis["loai_vi_pham"], 
        "Vi phạm phổ biến phòng thi", 
        "Loại vi phạm ở phòng thi",
        "green"
    )


# =========================================================
# 5. BIỂU ĐỒ - THẺ NỀN TRẮNG, BO TRÒN, KÍCH THƯỚC GỌN
# =========================================================

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
cl1, cl2 = st.columns(2, gap="medium")

with cl1:
    render_violation_bar_chart(
        start_date=start_date_str,
        end_date=end_date_str,
        session=cfg.SESSION_MAP["Phòng thường"],
        title="Phòng thường",
        number=1
    )

# =========================================================
# 6. DANH SÁCH VI PHẠM THEO CHẾ ĐỘ PHÒNG
# =========================================================
with cl2:
    render_violation_bar_chart(
        start_date=start_date_str,
        end_date=end_date_str,
        session=cfg.SESSION_MAP["Phòng thi"],
        title="Phòng thi",
        number=2
    )

# =========================================================
# 7. LỊCH SỬ SỰ CỐ / BIÊN BẢN (của tất cả người dùng)
# =========================================================
st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
tab_issue, tab_field = st.tabs(["Lịch sử sự cố", "Lịch sử biên bản"])
with tab_issue:
    render_request_list(
        _load_records("issue", all_users=True),
        kind="issue",
        key_prefix="stats_issue",
        can_approve=True,
    )
with tab_field:
    render_request_list(
        _load_records("field", all_users=True),
        kind="field",
        key_prefix="stats_field",
        can_approve=True,
    )
