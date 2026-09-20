import streamlit as st

st.set_page_config(layout="wide", page_title="Nhật ký vi phạm")


def show_logs():
    st.markdown(
        """
        <div class="page-header">
            <div>
                <h1 class="page-header-title">Nhật ký vi phạm</h1>
                <p class="page-header-subtitle">Lọc, xem chi tiết, duyệt, báo sai và xuất dữ liệu vi phạm.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.container(border=True):
        st.markdown("<h3 style='margin:0 0 10px;'>Bộ lọc</h3>", unsafe_allow_html=True)
        filter_col1, filter_col2, filter_col3, filter_col4, filter_col5 = st.columns(
            [2, 1.3, 2, 1.25, 1.55], gap="small"
        )
        with filter_col1:
            st.text_input("Tìm kiếm", placeholder="Tìm kiếm...", label_visibility="collapsed")
        with filter_col2:
            st.selectbox("Thời gian", ["Hôm nay", "Hôm qua", "7 ngày qua", "Tháng này"], label_visibility="collapsed")
        with filter_col3:
            st.selectbox(
                "Tòa nhà",
                ["Giảng đường Nguyễn Đăng - ND.202", "Giảng đường Alpha", "Nhà hành chính"],
                label_visibility="collapsed",
            )
        with filter_col4:
            st.selectbox("Phòng", ["ND.202", "ND.101", "ND.305"], label_visibility="collapsed")
        with filter_col5:
            st.selectbox(
                "Loại vi phạm",
                ["Tất cả", "Phá hoại cơ sở vật chất", "Trao đổi bài", "Sử dụng điện thoại"],
                label_visibility="collapsed",
            )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

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

    with st.container(border=True):
        h = st.columns([0.5, 2.5, 3, 2, 2])
        for col, title in zip(h, ["ID", "THÔNG TIN VI PHẠM", "THỜI GIAN & VỊ TRÍ", "BẰNG CHỨNG", "XÁC NHẬN"]):
            with col:
                st.caption(f"**{title}**")

        for item in data_violations:
            with st.container(border=True):
                cols = st.columns([0.5, 2.5, 3, 2, 2], gap="small")
                with cols[0]:
                    st.markdown(f"<span style='color:#8a95a2;font-weight:650;'>#{item['id']}</span>", unsafe_allow_html=True)
                with cols[1]:
                    st.markdown(
                        f"<strong>{item['title']}</strong><span class='ew-secondary-text'>{item['sub_title']}</span>",
                        unsafe_allow_html=True,
                    )
                with cols[2]:
                    st.markdown(
                        f"<strong>{item['time']}</strong><span class='ew-secondary-text'>{item['location']}</span>",
                        unsafe_allow_html=True,
                    )
                with cols[3]:
                    pc1, pc2 = st.columns([1, 1], gap="small")
                    with pc1:
                        st.image(item["img_placeholder"], width=60)
                    with pc2:
                        st.markdown(
                            f"<span class='ew-status pending'>{item['confidence']}</span>",
                            unsafe_allow_html=True,
                        )
                with cols[4]:
                    bc1, bc2 = st.columns(2, gap="small")
                    with bc1:
                        if st.button(":material/check:  Duyệt", key=f"accept_{item['id']}"):
                            st.success(f"Đã duyệt vi phạm số #{item['id']}")
                    with bc2:
                        if st.button(":material/close:  Báo sai", key=f"reject_{item['id']}"):
                            st.error(f"Đã báo sai AI dòng số #{item['id']}")
