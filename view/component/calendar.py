import streamlit as st
import calendar
from datetime import datetime

def render_calendar():
    today = datetime.today()

    year = today.year
    month = today.month

    month_name = calendar.month_name[month]

    # Thứ trong tuần: Monday -> Sunday
    weekdays = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

    calendar_html = f"""
    <div class="ew-calendar-card">

        <div class="ew-calendar-header">
            <button class="ew-calendar-arrow">◀</button>

            <strong>{month_name}</strong>

            <button class="ew-calendar-arrow">▶</button>
        </div>

        <div class="ew-calendar-grid ew-calendar-weekdays">
    """

    for day_name in weekdays:
        calendar_html += f"""
            <div class="ew-calendar-day ew-calendar-weekday">
                {day_name}
            </div>
        """

    calendar_html += """
        </div>

        <div class="ew-calendar-grid">
    """

    month_matrix = calendar.monthcalendar(year, month)

    for week in month_matrix:
        for day in week:

            if day == 0:
                calendar_html += """
                    <div class="ew-calendar-day ew-calendar-empty"></div>
                """
            else:

                active_class = (
                    " ew-calendar-active"
                    if day == today.day
                    else ""
                )

                calendar_html += f"""
                    <div class="ew-calendar-day{active_class}">
                        {day}
                    </div>
                """

    calendar_html += """
        </div>

    </div>
    """

    st.html(calendar_html)
