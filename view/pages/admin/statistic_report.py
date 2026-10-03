import pandas as pd
import streamlit as st
from datetime import datetime

from view.component.admin_table import render_admin_table
from view.component.calendar import render_calendar
from view.component.violation_chart import render_violation_type_chart

from src.database_query.violation_logs import (
    get_report_table,
    get_violation_report_kpis,
)


<<<<<<< HEAD
def show_report():

    # =========================================================
    # 1. CHỌN KHOẢNG THỜI GIAN
    # =========================================================

    period = st.segmented_control(
        "Thời gian",
        ("7 ngày", "12 tháng"),
        default="7 ngày",
        key="room_type",
        label_visibility="collapsed",
    )

    today = datetime.today()

    if period == "7 ngày":

        start_date = today - pd.Timedelta(days=6)
        end_date = today

    elif period == "12 tháng":

        start_date = (
            today.replace(day=1)
            - pd.DateOffset(months=11)
        )

        end_date = today

    else:
        return

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")


    # =========================================================
    # 2. LẤY KPI TỪ DATABASE
    # =========================================================

    kpis = get_violation_report_kpis(
        start_date=start_date_str,
        end_date=end_date_str,
    )


    # =========================================================
    # 3. LẤY DỮ LIỆU TABLE TỪ DATABASE
    # =========================================================

    table_rows = get_report_table(
        start_date=start_date_str,
        end_date=end_date_str,
    )


    session_map = {
        "exam": "Phòng thi",
        "study": "Phòng học",
    }


    table_data = [
        {
            "date": row["date"],
            "building": row["building"] or "--",
            "room": row["room"] or "--",

            "session": session_map.get(
                row["session"],
                row["session"] or "--",
            ),

            "total": int(
                row["total_violations"] or 0
            ),

            "confirmed": int(
                row["confirmed"] or 0
            ),

            "wrong": int(
                row["wrong"] or 0
            ),

            "pending": int(
                row["pending"] or 0
            ),
        }

        for row in table_rows
    ]


    # =========================================================
    # 4. KPI
    # =========================================================

    kpi1, kpi2, kpi3, kpi4 = st.columns(
        4,
        gap="medium",
    )

    with kpi1:
        st.metric(
            "Tổng log dự đoán",
            kpis["total_predictions"],
        )

    with kpi2:
        st.metric(
            "Đã báo đúng",
            kpis["confirmed"],
        )

    with kpi3:
        st.metric(
            "Báo sai AI",
            kpis["wrong"],
        )

    with kpi4:
        st.metric(
            "Chưa xác nhận",
            kpis["pending"],
        )


    # =========================================================
    # 5. CALENDAR + CHART
    # =========================================================

    st.markdown(
        "<div style='height:10px'></div>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(
        [1, 3],
        gap="medium",
    )

    with col1:
        render_calendar()

    with col2:
        render_violation_type_chart(
            start_date=start_date_str,
            end_date=end_date_str,
        )


    # =========================================================
    # 6. TABLE
    # =========================================================

    render_admin_table(
        "statistics",
        table_data,
        height=500,
    )
=======

# =========================================================
# 1. CHỌN KHOẢNG THỜI GIAN
# =========================================================

period = st.segmented_control(
    "Thời gian",
    ("7 ngày", "12 tháng"),
    default="7 ngày",
    key="room_type",
    label_visibility="collapsed",
)

today = datetime.today()

if period == "7 ngày":

    start_date = today - pd.Timedelta(days=6)
    end_date = today

elif period == "12 tháng":

    start_date = (
        today.replace(day=1)
        - pd.DateOffset(months=11)
    )

    end_date = today

else:
    st.error("Lỗi")

start_date_str = start_date.strftime("%Y-%m-%d")
end_date_str = end_date.strftime("%Y-%m-%d")


# =========================================================
# 2. LẤY KPI TỪ DATABASE
# =========================================================

kpis = get_violation_report_kpis(
    start_date=start_date_str,
    end_date=end_date_str,
)


# =========================================================
# 3. LẤY DỮ LIỆU TABLE TỪ DATABASE
# =========================================================

table_rows = get_report_table(
    start_date=start_date_str,
    end_date=end_date_str,
)


session_map = {
    "exam": "Phòng thi",
    "study": "Phòng học",
}


table_data = [
    {
        "date": row["date"],
        "building": row["building"] or "--",
        "room": row["room"] or "--",

        "session": session_map.get(
            row["session"],
            row["session"] or "--",
        ),

        "total": int(
            row["total_violations"] or 0
        ),

        "confirmed": int(
            row["confirmed"] or 0
        ),

        "wrong": int(
            row["wrong"] or 0
        ),

        "pending": int(
            row["pending"] or 0
        ),
    }

    for row in table_rows
]


# =========================================================
# 4. KPI
# =========================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(
    4,
    gap="medium",
)

with kpi1:
    st.metric(
        "Tổng log dự đoán",
        kpis["total_predictions"],
    )

with kpi2:
    st.metric(
        "Đã báo đúng",
        kpis["confirmed"],
    )

with kpi3:
    st.metric(
        "Báo sai AI",
        kpis["wrong"],
    )

with kpi4:
    st.metric(
        "Chưa xác nhận",
        kpis["pending"],
    )


# =========================================================
# 5. CALENDAR + CHART
# =========================================================

st.markdown(
    "<div style='height:10px'></div>",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(
    [1, 3],
    gap="medium",
)

with col1:
    render_calendar()

with col2:
    render_violation_type_chart(
        start_date=start_date_str,
        end_date=end_date_str,
    )


# =========================================================
# 6. TABLE
# =========================================================

render_admin_table(
    "statistics",
    table_data,
    height=500,
)
>>>>>>> 81d7401 (update)
