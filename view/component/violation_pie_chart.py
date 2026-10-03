from pathlib import Path
from html import escape

import streamlit as st

from src.database_query.violation_logs import (
    get_violation_type_distribution,
)


BASE_DIR = Path(__file__).resolve().parents[1]

ASSET_DIR = BASE_DIR / "asset"
STYLE_DIR = BASE_DIR / "style"


def _format_total(value: int) -> str:
    """
    Format số lượng vi phạm ở giữa Pie Chart.

    1284 -> 1.3k
    1200 -> 1.2k
    532  -> 532
    """

    if value >= 1000:
        return f"{value / 1000:.1f}k"

    return f"{value:,}"


COLORS = ["#006d3c", "#37bd74", "#4c6458", "#93ad9f"]
EMPTY_COLOR = "#e1e3e2"


def _build_gradient(data):
    """Tạo chuỗi color-stop cho conic-gradient, vd: '#006d3c 0% 40%, #37bd74 40% 100%'."""
    parts = []
    start = 0.0
    for index, item in enumerate(data):
        end = min(start + float(item["percentage"]), 100.0)
        parts.append(f"{COLORS[index % len(COLORS)]} {start:.2f}% {end:.2f}%")
        start = end
    return ", ".join(parts)


def _build_legend(data):
    """
    Tạo phần legend bên dưới Pie Chart.
    """

    colors = COLORS

    rows = []

    for index, item in enumerate(data):

        color = colors[
            index % len(colors)
        ]

        name = escape(
            str(item["type"])
        )

        percentage = item["percentage"]

        rows.append(
            f"""
            <div class="pie-row">

                <div class="pie-label">

                    <span
                        class="pie-dot"
                        style="background: {color};"
                    ></span>

                    <span>
                        {name}
                    </span>

                </div>

                <span class="pie-percentage">
                    {percentage:.0f}%
                </span>

            </div>
            """
        )

    return "".join(rows)


def render_violation_pie_chart(
    start_date: str,
    end_date: str,
):

    # ==========================================
    # 1. LẤY DỮ LIỆU DATABASE
    # ==========================================

    rows = get_violation_type_distribution(
        start_date=start_date,
        end_date=end_date,
    )

    total = sum(
        int(row["total"])
        for row in rows
    )


    # ==========================================
    # 2. KHÔNG CÓ DỮ LIỆU
    # ==========================================

    if total == 0:

        html_template = (
            ASSET_DIR
            / "violation_pie_chart.html"
        ).read_text(
            encoding="utf-8"
        )

        css = (
            STYLE_DIR
            / "violation_pie_chart.css"
        ).read_text(
            encoding="utf-8"
        )

        html = html_template

        html = html.replace(
            "{{GRADIENT}}",
            f"{EMPTY_COLOR} 0% 100%",
        )

        html = html.replace(
            "{{TOTAL}}",
            "0",
        )

        html = html.replace(
            "{{LEGEND}}",
            """
            <div class="pie-label">
                Chưa có dữ liệu vi phạm
            </div>
            """,
        )

        st.html(
            f"""
            <style>
                {css}
            </style>

            {html}
            """
        )

        return


    # ==========================================
    # 3. TÍNH PHẦN TRĂM
    # ==========================================

    data = []

    for row in rows:

        count = int(
            row["total"]
        )

        percentage = (
            count / total
        ) * 100

        data.append(
            {
                "type": row["type"],
                "total": count,
                "percentage": percentage,
            }
        )


    # ==========================================
    # 4. CHỈ GIỮ 3 LOẠI LỚN NHẤT
    #    CÁC LOẠI CÒN LẠI → KHÁC
    # ==========================================

    if len(data) > 3:

        top = data[:3]

        other_total = sum(
            item["total"]
            for item in data[3:]
        )

        if other_total > 0:

            top.append(
                {
                    "type": "Khác",
                    "total": other_total,
                    "percentage": (
                        other_total / total
                    ) * 100,
                }
            )

        data = top


    # ==========================================
    # 5. ĐỌC HTML
    # ==========================================

    html_template = (
        ASSET_DIR
        / "violation_pie_chart.html"
    ).read_text(
        encoding="utf-8"
    )


    # ==========================================
    # 6. ĐỌC CSS
    # ==========================================

    css = (
        STYLE_DIR
        / "violation_pie_chart.css"
    ).read_text(
        encoding="utf-8"
    )


    # ==========================================
    # 7. TẠO HTML ĐỘNG
    # ==========================================

    html = html_template

    html = html.replace(
        "{{GRADIENT}}",
        _build_gradient(data),
    )

    html = html.replace(
        "{{TOTAL}}",
        _format_total(total),
    )

    html = html.replace(
        "{{LEGEND}}",
        _build_legend(data),
    )


    # ==========================================
    # 8. RENDER
    # ==========================================

    st.html(
        f"""
        <style>
            {css}
        </style>

        {html}
        """
    )