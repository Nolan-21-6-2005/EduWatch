import altair as alt
import pandas as pd
import streamlit as st

from src.database_query.violation_logs import get_violation_trend


def render_line_chart(
    start_date: str,
    end_date: str,
    granularity: str = "day",
):
    """
    Biểu đồ đường số vi phạm theo thời gian, lấy từ DB.

    granularity: "day" | "month" | "hour" (xem get_violation_trend).
    """

    st.markdown(
        '<h4 class="ew-card-title">Xu hướng vi phạm</h4>',
        unsafe_allow_html=True,
    )

    data = get_violation_trend(start_date, end_date, granularity)
    df = pd.DataFrame(data)

    if df.empty or df["total"].sum() == 0:
        st.markdown(
            '<div class="ew-card-empty">Chưa có dữ liệu vi phạm trong khoảng này</div>',
            unsafe_allow_html=True,
        )
        return

    x_title = {"day": "Ngày", "month": "Tháng", "hour": "Giờ"}[granularity]

    chart = (
        alt.Chart(df)
        .mark_line(
            color="#006d3c",
            strokeWidth=3,
            interpolate="monotone",
            point=alt.OverlayMarkDef(
                filled=True,
                size=60,
                color="#006d3c",
            ),
        )
        .encode(
            # sort=None: giữ đúng thứ tự thời gian của DataFrame
            x=alt.X(
                "label:N",
                sort=None,
                title=None,
                axis=alt.Axis(
                    labelColor="#8A96A3",
                    labelFontSize=12,
                    labelAngle=0,
                    labelOverlap="greedy",
                    domain=False,
                    tickSize=0,
                ),
            ),
            y=alt.Y(
                "total:Q",
                title=None,
                scale=alt.Scale(domainMin=0),
                axis=alt.Axis(
                    labelColor="#8A96A3",
                    labelFontSize=12,
                    domain=False,
                    tickSize=0,
                    tickMinStep=1,
                    format="d",
                    grid=True,
                    gridColor="#EDF0F2",
                    gridWidth=1,
                ),
            ),
            tooltip=[
                alt.Tooltip("label:N", title=x_title),
                alt.Tooltip("total:Q", title="Số vi phạm"),
            ],
        )
        .properties(height=300)
        .configure_view(strokeWidth=0)
    )

    st.altair_chart(chart, width="stretch")
