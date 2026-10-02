import altair as alt
import pandas as pd
import streamlit as st

from streamlit_extras.chart_container import chart_container
from src.database_query.violation_chart import get_violation_type_statistics


def _build_violation_chart(
    df: pd.DataFrame,
) -> alt.Chart:

    bars = (
        alt.Chart(df)
        .mark_bar(
            cornerRadiusEnd=6,
            height=24,
        )
        .encode(
            y=alt.Y(
                "Loại vi phạm:N",
                sort="-x",
                title=None,
                axis=alt.Axis(
                    labelColor="#475569",
                    labelFontSize=12,
                    ticks=False,
                    domain=False,
                ),
            ),
            x=alt.X(
                "Số lần:Q",
                title=None,
                axis=alt.Axis(
                    labelColor="#94A3B8",
                    labelFontSize=11,
                    grid=True,
                    gridColor="#E9EEF2",
                    domain=False,
                    ticks=False,
                ),
            ),
            tooltip=[
                alt.Tooltip(
                    "Loại vi phạm:N",
                    title="Loại vi phạm",
                ),
                alt.Tooltip(
                    "Số lần:Q",
                    title="Số lần",
                ),
            ],
        )
    )

    labels = (
        alt.Chart(df)
        .mark_text(
            align="left",
            dx=6,
            color="#475569",
            fontSize=11,
        )
        .encode(
            y=alt.Y(
                "Loại vi phạm:N",
                sort="-x",
            ),
            x=alt.X("Số lần:Q"),
            text=alt.Text("Số lần:Q"),
        )
    )

    return (
        (bars + labels)
        .properties(
            height=max(220, len(df) * 38),
        )
        .configure_view(
            stroke=None,
        )
    )
    
def render_violation_type_chart(
    *,
    start_date: str,
    end_date: str,
):
    rows = get_violation_type_statistics(
        start_date=start_date,
        end_date=end_date,
    )

    if not rows:
        st.info("Chưa có dữ liệu vi phạm trong khoảng thời gian này.")
        return

    df = pd.DataFrame(rows)

    df = df.rename(
        columns={
            "session": "Phiên",
            "violation_type": "Loại vi phạm",
            "total": "Số lần",
        }
    )

    study_df = df[df["Phiên"] == "study"][
        ["Loại vi phạm", "Số lần"]
    ].copy()

    exam_df = df[df["Phiên"] == "exam"][
        ["Loại vi phạm", "Số lần"]
    ].copy()

    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown(
            '<div class="ew-chart-title">Phòng học</div>',
            unsafe_allow_html=True,
        )

        if study_df.empty:
            st.info("Chưa có dữ liệu phòng học.")
        else:
            study_chart = _build_violation_chart(study_df)

            with chart_container(study_df):
                st.altair_chart(
                    study_chart,
                    use_container_width=True,
                )

    with col2:
        st.markdown(
            '<div class="ew-chart-title">Phòng thi</div>',
            unsafe_allow_html=True,
        )

        if exam_df.empty:
            st.info("Chưa có dữ liệu phòng thi.")
        else:
            exam_chart = _build_violation_chart(exam_df)

            with chart_container(exam_df):
                st.altair_chart(
                    exam_chart,
                    use_container_width=True,
                )

