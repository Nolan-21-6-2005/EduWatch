import math
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


def _build_segments(data):
    radius = 16
    circumference = 2 * math.pi * radius

    colors = [
        "#006d3c",
        "#37bd74",
        "#4c6458",
        "#93ad9f",
    ]

    segments = []

    offset = 0

    for index, item in enumerate(data):

        percentage = float(item["percentage"])

        color = colors[index % len(colors)]

        # Trường hợp 100%
        if percentage >= 99.999:

            segments.append(
                f"""
                <circle
                    class="pie-segment"
                    cx="18"
                    cy="18"
                    r="{radius}"
                    stroke="{color}"
                    stroke-dasharray="{circumference} 0"
                    stroke-dashoffset="0"
                ></circle>
                """
            )

            segments.append(
                f"""
                <circle
                    cx="18"
                    cy="18"
                    r="16"
                    fill="none"
                    stroke="#006d3c"
                    stroke-width="3"
                    stroke-dasharray="100.53 0"
                ></circle>
                """
            )

            continue

        segment_length = (
            percentage / 100
        ) * circumference

        remaining_length = (
            circumference - segment_length
        )

        segments.append(
            f"""
            <circle
                class="pie-segment"
                cx="18"
                cy="18"
                r="{radius}"
                stroke="{color}"
                stroke-dasharray="
                    {segment_length}
                    {remaining_length}
                "
                stroke-dashoffset="-{offset}"
            ></circle>
            """
        )

        offset += segment_length

    return "".join(segments)

def _build_legend(data):
    """
    Tạo phần legend bên dưới Pie Chart.
    """

    colors = [
        "#006d3c",
        "#37bd74",
        "#4c6458",
        "#93ad9f",
    ]

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
            "{{PIE_SEGMENTS}}",
            "",
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
        "{{PIE_SEGMENTS}}",
        _build_segments(data),
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