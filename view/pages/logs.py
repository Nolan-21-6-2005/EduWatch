import streamlit as st
import pandas as pd

def show_logs():
    # --- CONFIG TRANG (Đặt ở đầu file) ---
    st.set_page_config(layout="wide", page_title="EduWatch VNUA - Nhật ký vi phạm")

    # --- 1. CHÈN CSS ĐỂ LÀM ĐẸP GIAO DIỆN (Nền xám nhạt, bo góc bộ lọc, màu sắc nút bấm) ---

    # --- 2. TIÊU ĐỀ TRANG & THANH CÔNG CỤ XUẤT DỮ LIỆU ---
    # Chia làm 2 cột: Cột trái chứa Tiêu đề, Cột phải chứa các nút Xuất dữ liệu gọn gàng
    head_col1, head_col2 = st.columns([3, 2])

    with head_col1:
        st.markdown(
            "<h1 style='margin-bottom: 0; font-size: 28px; font-weight: 700; color: #1a1a1a;'>Nhật ký vi phạm</h1>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='color: #707070; margin-top: 5px; font-size: 14px;'>Lọc, xem chi tiết, duyệt, báo sai AI, xóa và xuất dữ liệu vi phạm.</p>",
            unsafe_allow_html=True,
        )

    with head_col2:
        # Đẩy các nút sang sát lề phải giống hệt bản thiết kế
        st.write("")  # Tạo khoảng cách dọc nhẹ
        exp_col1, exp_col2, exp_col3 = st.columns([1, 1, 1])
        with exp_col1:
            st.button("📊 XUẤT CSV", use_container_width=True)
        with exp_col2:
            st.button(":material/picture_as_pdf: XUẤT PDF", use_container_width=True)
        with exp_col3:
            # Nút chính màu xanh lam nổi bật
            st.button("🗂️ XUẤT EXCEL", type="primary", use_container_width=True)


    # --- 3. KHU VỰC THÀNH PHẦN BỘ LỌC (FILTER BAR) ---
    # Dùng st.columns nằm ngang để tái hiện lại các thanh chọn tìm kiếm thông minh
    st.write("")
    filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(
        [2, 1.5, 2, 1.5, 1.5]
    )

    with filter_col1:
        search_query = st.text_input(
            label="Tìm kiếm", placeholder="Tìm kiếm...", label_visibility="collapsed"
        )
    with filter_col2:
        time_filter = st.selectbox(
            "Thời gian",
            ["Hôm nay", "Hôm qua", "7 ngày qua", "Tháng này"],
            label_visibility="collapsed",
        )
    with filter_col3:
        building_filter = st.selectbox(
            "Tòa nhà",
            ["Giảng đường Nguyễn Đăng - ND.202", "Giảng đường Alpha", "Nhà hành chính"],
            label_visibility="collapsed",
        )
    with filter_col4:
        room_filter = st.selectbox(
            "Phòng", ["ND.202", "ND.101", "ND.305"], label_visibility="collapsed"
        )
    with filter_col5:
        type_filter = st.selectbox(
            "Loại vi phạm",
            ["Tất cả", "Phá hoại cơ sở vật chất", "Trao đổi bài", "Sử dụng điện thoại"],
            label_visibility="collapsed",
        )


    # --- 4. DANH SÁCH DỮ LIỆU VI PHẠM (HIỂN THỊ DẠNG LIST CHUYÊN NGHIỆP) ---
    st.write("")

    # Giả lập nguồn dữ liệu (Bạn có thể map dữ liệu từ Database vào đây)
    data_violations = [
        {
            "id": 3,
            "title": "Phá hoại cơ sở vật chất",
            "sub_title": "Phòng học",
            "time": "08:30 AM - 24/05/2024",
            "location": "Giảng đường Nguyễn Đăng - ND.202",
            "confidence": "65%",
            "img_placeholder": "https://via.placeholder.com/50x30/1a3a2a/ffffff?text=Evidence",
        },
        {
            "id": 2,
            "title": "Trao đổi bài",
            "sub_title": "Phòng thi",
            "time": "09:12 AM - 24/05/2024",
            "location": "Giảng đường Nguyễn Đăng - ND.202",
            "confidence": "82%",
            "img_placeholder": "https://via.placeholder.com/50x30/1a3a2a/ffffff?text=Evidence",
        },
        {
            "id": 1,
            "title": "Sử dụng điện thoại",
            "sub_title": "Phòng thi",
            "time": "10:45 AM - 24/05/2024",
            "location": "Giảng đường Nguyễn Đăng - ND.202",
            "confidence": "94%",
            "img_placeholder": "https://via.placeholder.com/50x30/1a3a2a/ffffff?text=Evidence",
        },
    ]

    # Vẽ tiêu đề cột cho Bảng dữ liệu giống hình mẫu
    table_header_col = st.columns([0.5, 2.5, 3, 2, 2])
    with table_header_col[0]:
        st.caption("**ID**")
    with table_header_col[1]:
        st.caption("**THÔNG TIN VI PHẠM**")
    with table_header_col[2]:
        st.caption("**THỜI GIAN & VỊ TRÍ**")
    with table_header_col[3]:
        st.caption("**BẰNG CHỨNG**")
    with table_header_col[4]:
        st.caption("**XÁC NHẬN**")

    # Dùng vòng lặp duyệt qua data để render ra giao diện gọn gàng, khít và mượt mà
    for item in data_violations:
        # Sử dụng st.container có border mỏng bọc ngoài để tạo hiệu ứng dòng phẳng sạch sẽ
        with st.container(border=True):
            row_cols = st.columns([0.5, 2.5, 3, 2, 2])

            # Cột 1: ID
            with row_cols[0]:
                st.markdown(
                    f"<p style='color: #888888; margin-top: 10px;'>{item['id']}</p>",
                    unsafe_allow_html=True,
                )

            # Cột 2: Thông tin vi phạm
            with row_cols[1]:
                st.markdown(
                    f"<div style='margin-top: 2px;'><b style='font-size: 15px; color: #1a1a1a;'>{item['title']}</b><br><span style='color: #888888; font-size: 13px;'>{item['sub_title']}</span></div>",
                    unsafe_allow_html=True,
                )

            # Cột 3: Thời gian & vị trí
            with row_cols[2]:
                st.markdown(
                    f"<div style='margin-top: 2px;'><b style='font-size: 14px; color: #333333;'>{item['time']}</b><br><span style='color: #666666; font-size: 13px;'>{item['location']}</span></div>",
                    unsafe_allow_html=True,
                )

            # Cột 4: Bằng chứng (Ảnh chụp AI + Tỷ lệ % chính xác)
            with row_cols[3]:
                proof_col1, proof_col2 = st.columns([1, 1])
                with proof_col1:
                    # Giả lập hộp đen/ảnh cắt bằng chứng camera từ hệ thống AI
                    st.image(item["img_placeholder"], use_container_width=True)
                with proof_col2:
                    st.markdown(
                        f"<p class='confidence-tag' style='margin-top: 5px;'>{item['confidence']}</p>",
                        unsafe_allow_html=True,
                    )

            # Cột 5: Nút tương tác Duyệt / Báo sai
            with row_cols[4]:
                btn_col1, btn_col2 = st.columns([1, 1])
                with btn_col1:
                    # Mỗi dòng truyền kèm một key duy nhất (dựa trên ID) để tránh xung đột nút bấm
                    if st.button(
                        "DUYỆT", key=f"accept_{item['id']}", use_container_width=True
                    ):
                        st.success(f"Đã duyệt vi phạm số #{item['id']}")
                with btn_col2:
                    if st.button(
                        "BÁO SAI", key=f"reject_{item['id']}", use_container_width=True
                    ):
                        st.error(f"Đã báo sai AI dòng số #{item['id']}")
