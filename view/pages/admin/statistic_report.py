import pandas as pd
import streamlit as st
from datetime import datetime
from view.component.metric import kpi_metric

from view.component.violation_bar_chart import render_violation_bar_chart
from view.component.violation_list import render_violation_list

import src.database_query.violation_logs as vldb

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
        period = st.segmented_control(
            "Thời gian",
            ("7 ngày", "12 tháng"),
            default="7 ngày",
            key="type_selection",
            label_visibility="collapsed",
        )
    

today = datetime.today()

if period == "7 ngày":
    start_date = today - pd.Timedelta(days=6)
    end_date = today
elif period == "12 tháng":
    start_date = today.replace(day=1) - pd.DateOffset(months=11)
    end_date = today
else:
    st.error("Khoảng thời gian không hợp lệ")
    st.stop()

start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")


# =========================================================
# 2. LẤY DỮ LIỆU TỪ DATABASE THEO KHOẢNG THỜI GIAN
# =========================================================

kpis = vldb.get_violation_report_kpis(
    start_date=start_date_str,
    end_date=end_date_str,
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
# 3. CHUẨN BỊ DỮ LIỆU BẢNG
# =========================================================

session_map = {
    "exam": "Phòng thi",
    "study": "Phòng học",
}


# =========================================================
# 4. KPI
# =========================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")

with kpi1:
    kpi_metric(kpis["total_predictions"], "green")

with kpi2:
    kpi_metric(kpis["confirmed"], "green")

with kpi3:
    kpi_metric(kpis["wrong"], "green")

with kpi4:
    kpi_metric(kpis["pending"], "green")


# =========================================================
# 5. BIỂU ĐỒ - THẺ NỀN TRẮNG, BO TRÒN, KÍCH THƯỚC GỌN
# =========================================================

st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
cl1, cl2 = st.columns([1.9, 1], gap="medium")

with cl1:
    render_violation_bar_chart(
        start_date=start_date_str,
        end_date=end_date_str,
        period=period
    )

# =========================================================
# 6. DANH SÁCH VI PHẠM THEO CHẾ ĐỘ PHÒNG
# =========================================================
with cl2:

    render_violation_list(
        start_date=start_date_str,
        end_date=end_date_str,
    )
