import datetime

import pandas as pd
import streamlit as st

from view.component.admin_table import render_admin_table

st.set_page_config(layout="wide", page_title="EduWatch VNUA Admin")


def show_report():
    data = [
        {"date": "2026-05-27", "building": "Giảng đường A", "room": "ND.202", "Số vi phạm phòng thường": 3, "Số vi phạm phòng thi": 1},
        {"date": "2026-05-27", "building": "Giảng đường B", "room": "ND.206", "Số vi phạm phòng thường": 1, "Số vi phạm phòng thi": 4},
        {"date": "2026-05-27", "building": "Giảng đường Nguyễn Đăng", "room": "ND.202", "Số vi phạm phòng thường": 2, "Số vi phạm phòng thi": 0},
        {"date": "2026-05-27", "building": "Tòa nhà trung tâm", "room": "ND.206", "Số vi phạm phòng thường": 0, "Số vi phạm phòng thi": 2},
    ]

    df = pd.DataFrame(data)

    st.markdown(
        """
        <div class="page-header">
            <div>
                <h1 class="page-header-title">Thống kê báo cáo</h1>
                <p class="page-header-subtitle">Tổng hợp vi phạm theo tòa nhà và phòng học.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Cụm KPI: khoảng cách đều và cùng chiều cao.
    kpi1, kpi2 = st.columns(2, gap="medium")
    with kpi1:
        with st.container(border=True):
            st.metric("Vi phạm phòng thường", int(df["Số vi phạm phòng thường"].sum()))
    with kpi2:
        with st.container(border=True):
            st.metric("Vi phạm phòng thi", int(df["Số vi phạm phòng thi"].sum()))

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    render_admin_table(
        "statistics",
        [
            {
                "date": item["date"],
                "building": item["building"],
                "room": item["room"],
                "normal": item["Số vi phạm phòng thường"],
                "exam": item["Số vi phạm phòng thi"],
            }
            for item in data
        ],
        height=500,
    )
