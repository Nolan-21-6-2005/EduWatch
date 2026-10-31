import pandas as pd
import streamlit as st
import src.database_query.violation_logs as vldb

import utils.config as cfg
from datetime import datetime
from view.component.metric import kpi_metric
from view.component.violation_bar_chart import render_violation_bar_chart

st.set_page_config(
    page_title="Thống kê báo cáo",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# 1. CHỌN KHOẢNG THỜI GIAN
# =========================================================
col1, col2 = st.columns(2)
with col1:
    with st.container(horizontal=True, horizontal_alignment="left"):
        st.header("Thống kê báo cáo")
with col2:
    with st.container(horizontal=True, horizontal_alignment="right"):
        date_range = st.date_input(
            "KHOẢNG NGÀY",
            value=(cfg.start_date, cfg.end_date),
            format="DD/MM/YYYY",
            key="log_date_range",
        )
    
today = datetime.today()

start_date_str = cfg.start_date.strftime("%Y-%m-%d")
end_date_str = cfg.end_date.strftime("%Y-%m-%d")


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

table_rows = vldb.get_report_table(
    start_date=start_date_str,
    end_date=end_date_str,
)

# Dữ liệu này được dùng chung cho cả biểu đồ cột và doughnut.
# Mỗi loại vi phạm là một cột, giá trị là tổng log trong toàn bộ khoảng đã chọn.
violation_rows = vldb.get_violation_type_distribution(
    start_date=start_date_str,
    end_date=end_date_str,
)
violation_rows = [
    row for row in violation_rows
    if row.get("type") and int(row.get("total") or 0) > 0
]


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
        study_room_kpis["violation_type"], 
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
        exam_room_kpis["violation_type"], 
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
        date_range=date_range,
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
        date_range=date_range,
        number=2
    )
