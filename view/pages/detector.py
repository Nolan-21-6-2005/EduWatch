import streamlit as st

from src.frontend.camera_request import connect_camera


def show_detector():
    main_col, log_col = st.columns([2.15, 1], gap="small")

    with main_col:
        # Header của khu vực giám sát.
        with st.container(key="detector_header"):
            st.markdown(
                """
                <div class="detector-page-header">
                    <div>
                        <h1>Giám sát trực tiếp</h1>
                        <p>Theo dõi camera và điều khiển bộ phát hiện trong thời gian thực.</p>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Thanh tìm kiếm + bộ lọc dạng pill, đặt sát phía trên camera.
            with st.container(key="detector_filters"):
                filter_col1, filter_col2, filter_col3 = st.columns(
                    [1.35, 1, 1], gap="small"
                )

                with filter_col1:
                    st.text_input(
                        "Tìm kiếm thông tin",
                        placeholder="Tìm kiếm...",
                        label_visibility="collapsed",
                        key="detector_search",
                    )

                with filter_col2:
                    st.selectbox(
                        "Giảng đường",
                        ("Giảng đường ND", "Giảng đường A", "Giảng đường B"),
                        key="building",
                        label_visibility="collapsed",
                    )

                with filter_col3:
                    st.selectbox(
                        "Phòng",
                        ("ND101", "ND102"),
                        key="room",
                        label_visibility="collapsed",
                    )

        # Camera + thanh điều khiển được đặt trong cùng iframe.
        # Vì vậy control bar luôn nằm sát ngay dưới 4 khung hình.
        connect_camera()

    with log_col:
        # Nhật ký vi phạm tiếp tục là iframe riêng lấy dữ liệu từ FastAPI/SQLite.
        with st.container(key="log_list"):
            st.iframe(
                "http://localhost:8000/violations/panel",
                height=850
            )
