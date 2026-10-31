import streamlit as st
from datetime import datetime
from streamlit_extras.chartjs_chart import chartjs_chart
from src.database_query.violation_logs import get_violation_type_distribution

def render_violation_bar_chart(
    start_date: str,
    end_date: str,
    session: str,
    date_range,
    number: int
) -> None:
    
    violation_rows = get_violation_type_distribution(
        start_date=start_date,
        end_date=end_date,
        session=session
    )

    violation_rows = [
        row for row in violation_rows
        if row.get("type") and int(row.get("total") or 0) > 0
    ]
    
    with st.container(key=f"report_bar_card_'{number}'",height=410):
        st.markdown(
            '<div class="report-chart-title">Số lượng theo loại vi phạm</div>',
            unsafe_allow_html=True,
        )

        if not violation_rows:
            st.caption("Chưa có dữ liệu vi phạm trong khoảng thời gian này.")
        else:
            labels = [str(row["type"]) for row in violation_rows]
            values = [int(row["total"]) for row in violation_rows]
            green_palette = [
                "#2f6f46", "#4ca66b", "#7cc394", "#a8d9ba",
                "#cfe9d8", "#4C6458", "#93AD9F",
            ]
            bar_colors = [
                green_palette[index % len(green_palette)]
                for index in range(len(labels))
            ]

            bar_spec = {
                "type": "bar",
                "data": {
                    "labels": labels,
                    "datasets": [{
                        "label": "Số lần vi phạm",
                        "data": values,
                        "backgroundColor": bar_colors,
                        "hoverBackgroundColor": "#2f6f46",
                        "borderRadius": 6,
                        "borderSkipped": False,
                        "categoryPercentage": 0.72,
                        "barPercentage": 0.86,
                        "maxBarThickness": 78,
                    }],
                },
                "options": {
                    "responsive": True,
                    "maintainAspectRatio": False,
                    "plugins": {
                        "legend": {"display": False},
                    },
                    "scales": {
                        "x": {
                            "grid": {"display": False},
                            "ticks": {
                                "color": "#66736B",
                                "autoSkip": False,
                                "maxRotation": 35,
                                "minRotation": 0,
                            },
                        },
                        "y": {
                            "beginAtZero": True,
                            "ticks": {"precision": 0, "color": "#66736B"},
                            "grid": {"color": "rgba(76, 166, 107, 0.12)"},
                        },
                    },
                },
            }
            chartjs_chart(
                bar_spec,
                height=330,
                theme=None,
                key="report_violation_type_bar",
            )
