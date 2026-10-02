import streamlit as st

from src.database_query.violation_logs import get_violation_logs, violation_table_rows
from view.component.admin_table import render_admin_table

st.set_page_config(layout="wide", page_title="Nhật ký vi phạm")


def show_logs():
    # Bộ lọc lấy danh sách trực tiếp từ DB, không còn danh sách giả.
    all_rows = get_violation_logs()
    buildings = {row["building_id"]: row["ten_toa"] for row in all_rows if row["building_id"] is not None}
    rooms = {row["room_id"]: row["ten_phong"] for row in all_rows if row["room_id"] is not None}
    types = sorted({row["loai_vi_pham"] for row in all_rows if row["loai_vi_pham"]})
    statuses = {
        "pending": "Chờ xác nhận",
        "confirmed": "Đã xác nhận",
        "wrong": "Báo sai AI",
    }

    with st.container(border=True):
        st.markdown("<h3 style='margin:0 0 10px;'>Bộ lọc</h3>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns([2, 1.5, 1.5, 1.5], gap="small")

        with c1:
            building_options = {"Tất cả": None, **buildings}
            building_label = st.selectbox(
                "Tòa nhà",
                list(building_options.keys()),
                label_visibility="collapsed",
                key="violation_building",
            )
        with c2:
            room_options = {"Tất cả": None, **rooms}
            room_label = st.selectbox(
                "Phòng",
                list(room_options.keys()),
                label_visibility="collapsed",
                key="violation_room",
            )
        with c3:
            type_options = {"Tất cả": None, **{x: x for x in types}}
            type_label = st.selectbox(
                "Loại vi phạm",
                list(type_options.keys()),
                label_visibility="collapsed",
                key="violation_type",
            )
        with c4:
            status_label = st.selectbox(
                "Trạng thái",
                ["Tất cả", *statuses.values()],
                label_visibility="collapsed",
                key="violation_status",
            )

    status_value = next(
        (key for key, value in statuses.items() if value == status_label),
        None,
    )

    filtered_rows = get_violation_logs(
        building_id=building_options[building_label],
        room_id=room_options[room_label],
        violation_type=type_options[type_label],
        review_status=status_value,
    )

    # Chuyển các Row thành payload hiển thị cho HTML table.
    # Không có dữ liệu mock/placeholder ở đây.
    data = []
    from src.database_query.violation_logs import _image_data_uri
    from datetime import datetime
    
    c1, c2, c3 = st.columns(3, gap="small")
    
    total_confirmed_violation = sum(
        1
        for row in filtered_rows
        if (row["review_status"] or "pending") == "confirmed"
    )
    
    total_wrong_violation = sum(
        1
        for row in filtered_rows
        if (row["review_status"] or "pending") == "wrong"
    )
    
    average_confidence = (
        sum(float(row["confidence"] or 0) for row in filtered_rows)
        / len(filtered_rows)
        if filtered_rows
        else 0
    )
    
    
    with c1:
        st.html(
            f'''
            <div class="ew-bottom-stat">
                <div class="ew-bottom-icon green">♣</div>
                <div>
                    <span>Vi phạm báo đúng</span>
                    <strong>{total_confirmed_violation}</strong>
                    <small>Tổng số vi phạm báo đúng</small>
                </div>
            </div>
            ''',
        )

    with c2:
        st.html(
            f'''
            <div class="ew-bottom-stat">
                <div class="ew-bottom-icon blue">◆</div>
                <div>
                    <span>Vi phạm báo sai</span>
                    <strong>{total_wrong_violation}</strong>
                    <small>Tổng số vi phạm báo sai</small>
                </div>
            </div>
            ''',
        )

    with c3:
        st.html(
            f'''
            <div class="ew-bottom-stat">
                <div class="ew-bottom-icon orange">◇</div>
                <div>
                    <span>Độ chính xác</span>
                    <strong>{average_confidence}</strong>
                    <small>Mức tin cậy của AI</small>
                </div>
            </div>
            ''',
        )

    for row in filtered_rows:
        raw_time = str(row["thoi_gian"] or "")
        try:
            display_time = datetime.fromisoformat(
                raw_time.replace("T", " ")
            ).strftime("%d/%m/%Y %H:%M:%S")
        except ValueError:
            display_time = raw_time

        data.append(
            {
                "id": row["id"],
                "title": row["loai_vi_pham"] or "Vi phạm chưa xác định",
                "camera": row["vi_tri_goc"] or "Camera không xác định",
                "datetime_display": display_time,
                "thoi_gian": raw_time,
                "building": row["ten_toa"] or "--",
                "room": row["ten_phong"] or "--",
                "confidence": float(row["confidence"] or 0),
                "review_status": row["review_status"] or "pending",
                "image": _image_data_uri(row["image_path"]),
            }
        )

    render_admin_table("violations", data, height=690)
