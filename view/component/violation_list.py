"""Thẻ danh sách vi phạm theo chế độ phòng."""

from html import escape

import streamlit as st

from src.database_query.violation_logs import get_violation_type_distribution


_ICON_RULES = (
    (("đánh", "fight", "fighting"), "⚔", "#FCE8E6", "#B3261E"),
    (("làm phiền", "bother", "quấy rối"), "!", "#FFF3D6", "#946200"),
    (("phá hoại", "vandal", "hủy hoại"), "▧", "#FCE8E6", "#B3261E"),
    (("gian lận", "cheat", "under desk", "under-desk", "crawling"), "◉", "#E8F1FF", "#285DA8"),
)


def _violation_style(violation_type: str) -> tuple[str, str, str]:
    normalized = violation_type.casefold()
    for keywords, icon, background, foreground in _ICON_RULES:
        if any(keyword in normalized for keyword in keywords):
            return icon, background, foreground
    return "!", "#E7F5EB", "#287044"


def render_violation_list(*, start_date: str, end_date: str) -> None:
    """Hiển thị số lần vi phạm theo Phòng thi hoặc Phòng thường."""
    with st.container(key="ew_violation_list_card", height=410):
        control_col, _ = st.columns([1, 2.2], gap="small")
        with control_col:
            room_mode = st.selectbox(
                "Chế độ phòng",
                options=("Phòng thi", "Phòng thường"),
                index=0,
                key="ew_violation_list_session",
                label_visibility="collapsed",
            )

        session = "exam" if room_mode == "Phòng thi" else "study"
        rows = get_violation_type_distribution(
            start_date=start_date,
            end_date=end_date,
            session=session,
        )
        rows = [
            row for row in rows
            if row.get("type") and int(row.get("total") or 0) > 0
        ]

        st.markdown(
            """
            <div class="ew-violation-list-heading">Danh sách vi phạm</div>
            <div class="ew-violation-list-subtitle">Số lần ghi nhận theo từng loại vi phạm</div>
            """,
            unsafe_allow_html=True,
        )

        if not rows:
            st.markdown(
                '<div class="ew-violation-list-empty">Chưa có vi phạm trong chế độ phòng và khoảng thời gian đã chọn.</div>',
                unsafe_allow_html=True,
            )
            return

        items = []
        for row in rows:
            name = str(row["type"])
            total = int(row["total"] or 0)
            icon, icon_bg, icon_fg = _violation_style(name)
            items.append(
                f"""
                <div class="ew-violation-list-row">
                    <div class="ew-violation-list-icon" style="background:{icon_bg};color:{icon_fg};">
                        <span>{icon}</span>
                    </div>
                    <div class="ew-violation-list-name">{escape(name)}</div>
                    <div class="ew-violation-list-count">{total}</div>
                </div>
                """
            )

        st.markdown(
            '<div class="ew-violation-list-items">' + "".join(items) + "</div>",
            unsafe_allow_html=True,
        )
