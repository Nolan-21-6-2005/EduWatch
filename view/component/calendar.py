import calendar
from datetime import date

import streamlit as st

from src.database_query.violation_logs import get_active_days

WEEKDAYS = ["T2", "T3", "T4", "T5", "T6", "T7", "CN"]

_KEY_YEAR = "cal_year"
_KEY_MONTH = "cal_month"
_KEY_SELECTED = "cal_selected"


# ---------------------------------------------------------
# State + callbacks
# ---------------------------------------------------------

def _init_state():
    today = date.today()
    st.session_state.setdefault(_KEY_YEAR, today.year)
    st.session_state.setdefault(_KEY_MONTH, today.month)
    st.session_state.setdefault(_KEY_SELECTED, None)


def _shift_month(delta: int):
    index = st.session_state[_KEY_YEAR] * 12 + (st.session_state[_KEY_MONTH] - 1) + delta
    st.session_state[_KEY_YEAR] = index // 12
    st.session_state[_KEY_MONTH] = index % 12 + 1


def _go_today():
    today = date.today()
    st.session_state[_KEY_YEAR] = today.year
    st.session_state[_KEY_MONTH] = today.month
    st.session_state[_KEY_SELECTED] = None


def _toggle_day(day: date):
    # Bấm lại đúng ngày đang chọn -> bỏ chọn
    if st.session_state[_KEY_SELECTED] == day:
        st.session_state[_KEY_SELECTED] = None
    else:
        st.session_state[_KEY_SELECTED] = day


def _clear_selection():
    st.session_state[_KEY_SELECTED] = None


def _day_key(day: date) -> str:
    return f"cal_{day:%Y%m%d}"


def _marker_css(year: int, month: int, active_days: set[int]) -> str:
    """CSS riêng cho tháng đang xem: đánh dấu hôm nay và ngày có vi phạm."""
    rules = []
    today = date.today()

    if (today.year, today.month) == (year, month):
        rules.append(f".st-key-{_day_key(today)} button {{ border-color: #20a85d !important; }}")

    for d in active_days:
        rules.append(
            f".st-key-{_day_key(date(year, month, d))} button::after "
            "{ content: ''; position: absolute; bottom: 4px; left: 50%; width: 5px; height: 5px; "
            "margin-left: -2.5px; border-radius: 50%; background: #20a85d; }"
        )

    return "<style>" + "\n".join(rules) + "</style>"


# ---------------------------------------------------------
# Render
# ---------------------------------------------------------

def render_calendar() -> date | None:
    """
    Lịch tương tác. Trả về ngày đang được chọn (hoặc None nếu chưa chọn).

    - ◀ / ▶: chuyển tháng
    - Bấm vào ngày: chọn ngày (bấm lại để bỏ chọn)
    - Chấm xanh dưới số ngày: ngày có phát sinh log vi phạm ("ngày làm việc")
    - Viền xanh: hôm nay
    """
    _init_state()

    year = st.session_state[_KEY_YEAR]
    month = st.session_state[_KEY_MONTH]
    selected = st.session_state[_KEY_SELECTED]

    active_days = get_active_days(year, month)
    st.markdown(_marker_css(year, month, active_days), unsafe_allow_html=True)

    # ----- Header: ◀ Tháng 10, 2026 ▶ -----
    prev_col, title_col, next_col = st.columns([1, 3, 1], vertical_alignment="center", gap="xxsmall")
    with prev_col:
        st.button(
            ":material/chevron_left:",
            key="cal_prev",
            type="tertiary",
            on_click=_shift_month,
            args=(-1,),
            help="Tháng trước",
        )
    with title_col:
        st.markdown(
            f'<h4 class="ew-card-title ew-cal-title">Tháng {month}, {year}</h4>',
            unsafe_allow_html=True,
        )
    with next_col:
        st.button(
            ":material/chevron_right:",
            key="cal_next",
            type="tertiary",
            on_click=_shift_month,
            args=(1,),
            help="Tháng sau",
        )

    # ----- Hàng thứ -----
    head_cols = st.columns(7, gap="xxsmall")
    for col, name in zip(head_cols, WEEKDAYS):
        col.markdown(f'<div class="ew-cal-weekday">{name}</div>', unsafe_allow_html=True)

    # ----- Lưới ngày -----
    for week in calendar.Calendar(firstweekday=0).monthdayscalendar(year, month):
        cols = st.columns(7, gap="xxsmall")
        for index, (col, day_number) in enumerate(zip(cols, week)):
            if day_number == 0:
                continue

            day = date(year, month, day_number)
            is_weekend = index >= 5
            col.button(
                str(day_number),
                key=_day_key(day),
                type="primary" if day == selected else "tertiary",
                on_click=_toggle_day,
                args=(day,),
                width="stretch",
                help="Ngày cuối tuần" if is_weekend else None,
            )

    # ----- Chân lịch -----
    foot_left, foot_right = st.columns(2, gap="xxsmall")
    with foot_left:
        st.button("Hôm nay", key="cal_today", type="tertiary", on_click=_go_today, width="stretch")
    with foot_right:
        if selected:
            st.button(
                "Bỏ chọn ngày",
                key="cal_clear",
                type="tertiary",
                on_click=_clear_selection,
                width="stretch",
            )

    st.markdown(
        '<div class="ew-cal-legend"><span class="ew-cal-dot"></span> Ngày có log vi phạm</div>',
        unsafe_allow_html=True,
    )

    return selected
